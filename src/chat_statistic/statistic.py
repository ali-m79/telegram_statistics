from pathlib import Path
from typing import Union

from hazm import Normalizer
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud
from src.utils.io import read_file, read_json


class ChatStatistic():
    """Generate Chat Statistic From Telegram Chat Json File
    """
    def __init__(self, chat_json: Union[str, Path]):
        """
        Args:
            chat_json: Path To Telegram Export Json File
        """
        # load json data
        logger.info(f"loading chat data from {chat_json}")
        self.chat_data = read_json(chat_json)
        self.normalizer = Normalizer()

        # load stopwords
        logger.info(f"loadinf stopwords from {DATA_DIR/'stopwords.txt'}")
        stopwords = read_file(DATA_DIR / "stopwords.txt").split("\n")
        self.stopwords = list(map(self.normalizer.normalize, stopwords))

    def generate_word_cloud(
        self,
        output_dir: Union[str, Path],
        width: int = 800, height: int = 600,
        max_font_size: int = 250,
        background_color: str = "white",
    ):
        """Generate a Word Cloud From Chat Data
        Args:
            output_dir : path to output directory for word cloud image
        """

        # read a text content of messages
        logger.info("loading text contents")
        text_content = ""
        for msg in self.chat_data["messages"]:
            if type(msg["text"]) is str:
                text_content += msg["text"]
            else:
                for sub_msg in msg["text"]:
                    if isinstance(sub_msg, str):
                        text_content += sub_msg
                    elif "text" in sub_msg:
                        text_content += sub_msg["text"]

        # Normalize for final word cloud
        text_content = self.normalizer.normalize(text_content)

        # generate final word cloud
        logger.info("Generating word cloud")
        wordcloud = WordCloud(
            background_color=background_color,
            height=height, width=width,
            max_font_size=max_font_size,
            font_path=str(DATA_DIR / "./Vazir-Code.ttf"),
            stopwords=self.stopwords,
            ).generate(text_content)

        # Save word cloud in png format
        logger.info(f"saving word cloud to {output_dir}")
        wordcloud.to_file(Path(output_dir) / "wordcloud.png")


if __name__ == "__main__":
    chat_stat = ChatStatistic(chat_json=DATA_DIR / "stack.json")
    chat_stat.generate_word_cloud(output_dir=DATA_DIR)
    print("done!")
