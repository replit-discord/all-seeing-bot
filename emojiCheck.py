import re
import emoji
def count(message):
	emoji_list = [c for c in message if c in emoji.UNICODE_EMOJI]
	emoji_list += re.findall(r'<:\w*:\d*>', message)
	return len(emoji_list)