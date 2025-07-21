# 📦 MAL-Stremio DB Updater

Repository for the update script for the MAL-Stremio Addon.

It fetches anime mapping metadata from [Anime-Lists](https://github.com/Fribb/anime-lists?tab=readme-ov-file) and
updates the mapping database used by the addon. The
script can be run periodically as a cron job to keep the data up to date.

## 📋 Requirements

- Python 3.9+
- MongoDB
- Pipenv (optional)
- Dependencies in Pipfile and requirements.txt

## ⚙️ Setup

1. Clone the repository.  
2. Create a `.env` file with the required environment variables (Refer to the `.env.example` file).  
3. Install dependencies using Pipenv or Pip.

## 🚀 Usage

```bash
flask run
# or 
python run.py
```

## 🙏 Acknowledgements

- [Fribb](https://github.com/Fribb): Creator of the Anime-Lists mapping project which this script fetches data from.