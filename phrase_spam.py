def _is_repeating(message, repeating_count):
    for i in range(len(message) // repeating_count):
        m = message[:i + 1]

        if m == '':
            continue

        spammed_count = [0]
        for i in range(len(message) // len(m)):
            if message[i * len(m):(i + 1) * len(m)] == m:
                spammed_count[-1] += 1
            else:
                if spammed_count[-1] != 0:
                    spammed_count.append(0)
        if max(spammed_count) >= repeating_count:

            return True
    return False


def is_repeating(message, repeating_count=5, ignore_chars=('\t\t', ' ')):
    for c in ignore_chars:
        message = message.replace(c, '')
    message_new = ''
    for m in message:
        message_new += m
    message = message_new
    for i in range(len(message)):
        r = _is_repeating(message[i:], repeating_count)
        if r:
            return True
    return False
