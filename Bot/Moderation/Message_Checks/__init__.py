
from Moderation.Message_Checks import banned_word, emoji_spam, illegal_char, invite, link, mention_spam, spam


checks = [
    banned_word, spam,
    emoji_spam, illegal_char,
    invite, link, mention_spam
]

check_names = [c.name for c in checks]
