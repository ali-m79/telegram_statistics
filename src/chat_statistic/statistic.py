from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import seaborn as sns
from hazm import Normalizer, sent_tokenize
from loguru import logger
from src.data import DATA_DIR
from src.utils.io import read_file, read_json
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
        self.chat_data = read_json(chat_json)
        self.normalizer = Normalizer()

        # load stopwords
        logger.info(f"loadinf stopwords from {DATA_DIR/'stopwords.txt'}")
        stopwords = read_file(DATA_DIR / "stopwords.txt").split("\n")
        self.stopwords = list(map(self.normalizer.normalize, stopwords))

    @staticmethod
    def rebuild_msg(sub_message: list) -> str:
        """rebuild a composite messages, include tag, link, hashtag and etc
        """
        text = ""
        for sub_msg in sub_message:
            if isinstance(sub_msg, str):
                text += sub_msg
            elif "text" in sub_msg:
                text += sub_msg["text"]

        return text

    def msg_has_question(self, msg) -> bool:
        """check if the message have question
        """
        if not isinstance(msg["text"], str):
            msg["text"] = self.rebuild_msg(msg["text"])

        sentences = sent_tokenize(msg["text"])
        for sent in sentences:
            if ("?" not in sent) and ("؟" not in sent):
                continue

            return True

    def get_top_users(self, top_n: int = 10) -> dict:
        """Gets the top n users from chat based on replying question from other
        """
        # check messages for question
        is_question = defaultdict(bool)
        for msg in self.chat_data["messages"]:
            if not msg.get("text"):
                continue

            is_question[msg["id"]] = self.msg_has_question(msg)

        # get top users based on replying question
        users = []
        for msg in self.chat_data["messages"]:
            if not msg.get("reply_to_message_id"):
                continue

            if not is_question[msg["reply_to_message_id"]]:
                continue
            users.append(msg["from"])

        top_users = dict(Counter(users).most_common(top_n))

        fig, ax = plt.subplots(figsize=(top_n, top_n * 0.5))
        ax.set(
            title=f'Top {top_n} Users in Replying to Questions',
            xlabel='Number of Replies',
            ylabel='User',
        )
        sns.set(font_scale=3, style='whitegrid')
        sns.barplot(
            y=list(top_users.keys()), x=list(top_users.values()),
            ax=ax
        )
        fig.savefig(DATA_DIR / 'top_users.png', dpi=500)

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
                text_content += self.rebuild_msg(msg["text"])

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
    chat_stat = ChatStatistic(chat_json=DATA_DIR / "online.json")
    chat_stat.generate_word_cloud(output_dir=DATA_DIR)
    chat_stat.get_top_users(10)
    print("done!")
