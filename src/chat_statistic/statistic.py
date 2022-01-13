import json
from pathlib import Path
from typing import Union

import arabic_reshaper
# from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


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
        with open(chat_json) as f:
            self.chat_data = json.load(f)
        self.normalizer = Normalizer()

        # load stopwords
        logger.info(f"loadinf stop words from {DATA_DIR/'stopwords.txt'}")
        stopwords = open(DATA_DIR / "stopwords.txt").readlines()
        stopwords = list(map(str.strip, stopwords))
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
                tokens = word_tokenize(msg["text"])
                tokens = list(filter(lambda x: x not in self.stopwords, tokens))
                text_content += f"{' '.join(tokens)} "

        # Normalize and reshape for final word cloud
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        # text_content = get_display(text_content)

        # generate final word cloud
        logger.info("Generating word cloud")
        wordcloud = WordCloud(
            background_color=background_color,
            height=height, width=width,
            max_font_size=max_font_size,
            font_path=str(DATA_DIR / "./Vazir.ttf"),
            ).generate(text_content)

        # Save word cloud in png format
        logger.info(f"saving word cloud to {output_dir}")
        wordcloud.to_file(Path(output_dir) / "wordcloud.png")


if __name__ == "__main__":
    chat_stat = ChatStatistic(chat_json=DATA_DIR / "markaz.json")
    chat_stat.generate_word_cloud(output_dir=DATA_DIR)
    print("done!")
