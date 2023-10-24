from langchain.utilities import SQLDatabase
from langchain import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import streamlit as st
from sqlalchemy import create_engine


def get_llm():
    return ChatOpenAI(temperature=0, openai_api_key=st.secrets["OPENAI_API_KEY"])

def get_sql_engine():
    host = ''
    username = ''
    password = ''
    database_schema = 'dbschema'

    return create_engine(f'postgresql+psycopg2://{username}:{password}@{host}/{database_schema}')

def get_schema():
    cols = ["id", "first_name", "last_name", "title", "address1", "city", "state", "zip", "country", "phone", "email", "birthdate"]
    schemas = []
    for c in cols:
        schemas.append(f"\n dbschema.contacts.{c}")
    catalog = ",".join(schemas)

    cols = (', '.join('"' + item + '"' for item in cols))
    return cols, catalog

def generate(query: str) -> str:
    llm = get_llm()
    engine = get_sql_engine()
    cols, catalog = get_schema()

    prompt_template = """ Given an input question, first create a postgrsql-style query to run, 
        then look at the results of the query and return the answer.

        use the below columns for given question
        {input} \n
        """+catalog+""" 

            Only use the User table to generate the query:

            Only use the following Column names: \n
          """+ cols +""" 
        
             
        Examples of question and expected SQLQuery
        Question: "What is the date of birthday of virat kohli?
        SQLQuery: SELECT "birthdate" FROM dbschema."contacts" WHERE "first_name" = 'virat' AND "last_name" = 'kohli';

        Write a postgreSQL query for Question: {input}
        Only return the answer to user based on SQLResult of query
        """

    db = SQLDatabase(engine)

    PROMPT_sql = PromptTemplate(
        input_variables=["input" , "dialect"], template=prompt_template
    )

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT_sql, verbose=False)

    response = db_chain(query)
    if "Answer" in response:
        return response['Answer']
    if "result" in response:
        return response['result']
    else:
        return response