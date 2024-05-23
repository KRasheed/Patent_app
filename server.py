import warnings
import uvicorn

from app.Utils.get_secrets import get_and_set_secrets

get_and_set_secrets()

# Load environment variables from .env file
# from dotenv import load_dotenv
# load_dotenv()

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=5000, workers=1)
