import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import weaviate
from weaviate.util import generate_uuid5
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.exceptions import WeaviateBaseError
# from dotenv import load_dotenv

# load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s\n")

class WeaviateSyncer:
    def __init__(self):
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.environ["WEAVIATE_URL"],
            auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
            headers={'X-OpenAI-Api-key': os.environ["OPENAI_API_KEY"]}
        )

    def ensure_collection(self, name: str, properties: List[Property]):
        if self.client.collections.exists(name):
            logging.info(f"Collection '{name}' already exists")
            return
        else:
            self.client.collections.create(
                name=name,
                vector_config=Configure.Vectors.text2vec_openai(
                    model="text-embedding-3-small"
                ),
                properties=properties
            )
            logging.info(f"Created collection '{name}'")

    def get_existing_uuids(self, collection_name: str, batch_size: int = 100) -> Set[str]:
        collection = self.client.collections.get(collection_name)
        uuids = set()
        offset = 0

        while True:
            response = collection.query.fetch_objects(limit=batch_size, offset=offset)
            objects = response.objects
            if not objects:
                break
            for obj in objects:
                uuids.add(str(obj.uuid))
            offset += len(objects)

        return uuids

    def upsert_entry(self, collection_name: str, properties: Dict[str, Any], uuid_key: str):
        collection = self.client.collections.get(collection_name)
        stable_id = properties[uuid_key].strip().lower()
        uuid = generate_uuid5(stable_id)

        try:
            collection.data.insert(properties=properties, uuid=uuid)
            logging.info(f"Inserted: {properties.get(uuid_key, '')[:50]} (UUID: {uuid})")
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if "already exists" in str(e):
                collection.data.update(uuid=uuid, properties=properties)
                logging.info(f"Updated: {properties.get(uuid_key, '')[:50]} (UUID: {uuid})")
            else:
                logging.error(f"Error inserting: {e}")

        return uuid

    def delete_entry(self, collection_name: str, uuid: str, name_field: str):
        collection = self.client.collections.get(collection_name)
        try:
            obj = collection.query.fetch_object_by_id(uuid)
            name = obj.properties.get(name_field, "<unknown>") if obj else "<missing>"
            logging.info(f"Deleting: {name} (UUID: {uuid})")
            collection.data.delete_by_id(uuid)
        except WeaviateBaseError as e:
            logging.error(f"Failed to delete {uuid}: {e}")

    def sync_entries(self, collection_name: str, schema_props: List[Property], entries: List[Dict[str, Any]], uuid_key: str):
        self.ensure_collection(collection_name, schema_props)

        # Upsert all entries and collect current UUIDs
        current_uuids = set()
        for entry in entries:
            uuid = self.upsert_entry(collection_name, entry, uuid_key)
            current_uuids.add(uuid)

        # Get what's currently in DB (after upserts)
        existing_uuids = self.get_existing_uuids(collection_name)
        logging.info(f"Existing uuids: {existing_uuids}")
        logging.info(f"Current uuids: {current_uuids}")
        to_delete = existing_uuids - current_uuids
        logging.info(f"UUIDs to delete: {to_delete}")

        # Delete what's no longer present
        for uuid in to_delete:
            self.delete_entry(collection_name, uuid, uuid_key)

    def close(self):
        self.client.close()


def main():
    syncer = WeaviateSyncer()
    try:
        # --- FAQ Sync ---
        qa_props = [
            Property(name="question", data_type=DataType.TEXT),
            Property(name="answer", data_type=DataType.TEXT),
            Property(name="source", data_type=DataType.TEXT),
            Property(name="tags", data_type=DataType.TEXT_ARRAY)
        ]
        faq_path = Path(__file__).resolve().parent / "docs" / "faq" / "general.json"
        if faq_path.exists():
            with faq_path.open(encoding="utf-8") as f:
                faq_entries = json.load(f)
            syncer.sync_entries("QAEntry", qa_props, faq_entries, "question")
        else:
            logging.warning(f"FAQ file not found: {faq_path}")

        # --- Tooltip Sync ---
        tooltip_props = [
            Property(name="term", data_type=DataType.TEXT),
            Property(name="headline", data_type=DataType.TEXT),
            Property(name="definition", data_type=DataType.TEXT),
            Property(name="link", data_type=DataType.TEXT)
        ]
        tooltip_path = Path(__file__).resolve().parent / "docs" / "tooltips.json"
        if tooltip_path.exists():
            with tooltip_path.open(encoding="utf-8") as f:
                tooltip_entries = json.load(f)
            syncer.sync_entries("Tooltip", tooltip_props, tooltip_entries, "term")
        else:
            logging.warning(f"Tooltip file not found: {tooltip_path}")

    finally:
        syncer.close()

if __name__ == "__main__":
    main()
