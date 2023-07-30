from streamlit.connections import ExperimentalBaseConnection
import pinecone
import json
import openai
import streamlit as st


class PineconeDBConnection(ExperimentalBaseConnection):
    def _connect(self, **kwargs):
        # Implement the connection setup here.
        # get params from secret
        api_key = kwargs.get('api_key', None) or self._secrets['api_key']
        environment = kwargs.get('environment', None) or self._secrets['environment']
        # all connection params
        if api_key and environment is not None:
            try:
                pinecone.init(api_key=api_key, environment=environment)
            except Exception as e:
                return 'Did you forget to set the environment and key?'

    def fetch_inds(self):
        inds = pinecone.list_indexes()
        return inds

    def describe_inds(self, index_name: str):
        description = pinecone.describe_index(index_name)
        return description

    def delete_inds(self, index_name: str):
        pinecone.delete_index(index_name)


    @staticmethod
    @st.cache_data(ttl=1.0)
    def query(index_name: str, question: str):
        res = openai.Embedding.create(
            input=[question],
            engine="text-embedding-ada-002"
        )

        vec = res['data'][0]['embedding']
        pinecone_index = pinecone.Index(index_name)
        # retrieve from Pinecone
        res = pinecone_index.query(vec, top_k=2, include_metadata=True)
        # get relevant contexts (including the questions)
        out = (json.loads(res['matches'][0]['metadata']['_node_content']))
        return out['text']
