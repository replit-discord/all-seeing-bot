class ImmutableList(list):

    def _immutable(self, *args, **kws):
        raise TypeError('This list is immutable!')

    pop = _immutable
    remove = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    reverse = _immutable


# Just a note: I dont use this anymore.

perms = ImmutableList([
    'manage_server',
    'trustrole',
    'untrustrole',
    'muterole',
    'setoffenseduration',
    'setmuteduration',
    'offenselimit',
    'emojimax',
    'mentionlimit',
    'muteincrement',
    'phraselimit',
    'actionlog',
    'modmail',
    'reset',
    'togglelist',
    'rtogglelist',
    'togglechannel',
    'rtogglechannel',
    'prefix',
    'setchannel',
    'fix',
    'leaderboard',
    'setmin',
    'banword',
    'unbanword',
    'banreaction',
    'unbanreaction',
    'banlist',
    'kick',
    'ban',
    'unban',
    'mute',
    'unmute',
    'warn',
    'warns',
    'removewarn',
    'purge',
    'roll',
    'coinflip',
    'help',
    'mail',
    'munban',
    'bypass'
])


class Permissions:

    def __init__(self, p=0):
        if not isinstance(p, int):
            raise TypeError(
                f'Expected int parameter, received {p.__class__.__name__} instead.')

        self.value = p

    def keys(self):
        return perms

    def __getitem__(self, p):
        if p not in perms:
            raise KeyError(f'{p} is not a valid permission!')
        return self._bit(perms.index(p))

    def __setitem__(self, p, value):
        if p not in perms:
            raise KeyError(f'{p} is not a valid permission!')
        if not isinstance(value, bool):
            raise TypeError(
                f'Expected bool paramater, received {value.__class__.__name__} instead.')
        self._set(perms.index(p), value)

    def _bit(self, pos):
        return bool((self.value >> pos) & 1)

    def _set(self, pos, allowed):
        if allowed:
            self.value |= (1 << pos)
            return
        self.value &= ~(1 << pos)

    @property
    def perms(self):
        return [p for p in perms if self._bit(perms.index(p))]


def generate_perms(enabled_perms=[]):
    permissions = Permissions()
    for p in enabled_perms:
        if p not in perms:
            raise KeyError(f'{p} is not a valid permission!')

        permissions._set(perms.index(p), True)
    return permissions


for perm in perms:
    perms = perms
    get_func = eval(f'lambda self: self._bit({perms.index(perm)})')
    set_func = eval(
        f'lambda self, value: self._set({perms.index(perm)}, value)')
    setattr(Permissions, perm, property(get_func, set_func))

    del set_func, get_func
