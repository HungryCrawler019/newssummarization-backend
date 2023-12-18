from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    JWT_PRIVATE_KEY: str
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX: str

    class Config:
        env_file = './.env'


settings = Settings()