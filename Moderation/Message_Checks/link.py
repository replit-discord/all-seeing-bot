from re import findall

default = False
check_name = 'Link check'


async def check(message):
	links = findall(
		r'''(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<'
		'>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|['
		'^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?''',
		message.content
	)
