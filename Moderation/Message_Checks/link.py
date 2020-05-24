from re import findall

default = False
check_name = 'Link check'
name = 'link'


async def check(message):
    words = message.content.split(' ')
    links = []
    for w in words:
        links += findall(
            r'^[[(]?((http|ftp|https)://)([\w_-]+(?:(?:\.[\w_-]+)+))('
            r'[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?[\])]?',
            w
        )
    print(links)
    if len(links) > 0:
        return True
    return False
