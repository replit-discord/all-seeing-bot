from flask_wtf import FlaskForm, CsrfProtect
from wtforms import BooleanField, FieldList, FormField, SubmitField


class PermField(FlaskForm):
    check = BooleanField(
        ''
    )


class PermForm(FlaskForm):
    perms = FieldList(
        FormField(PermField)
    )
    submit = SubmitField('Save changes', render_kw={
                         'class': "btn btn-primary input-group-btn p-centered"})


class CommandField(FlaskForm):
    check = BooleanField(
        ''
    )


class CogField(FlaskForm):
    commands = FieldList(
        FormField(PermField)
    )


class CommandsForm(FlaskForm):
    cogs = FieldList(
        FormField(CogField)
    )
    submit = SubmitField('Save changes', render_kw={
                         'class': "btn btn-primary input-group-btn p-centered"})


def generate_perm_field(perms):

    perms.sort(key=lambda x: x[0])
    form = PermForm()
    a = 0
    for perm in perms:
        perm_field = PermField()
        perm_field.check.label = perm[0]
        perm_field.check.data = perm[1]

        perm_field.check.name = f'perms-{a}-{perm[2]}'
        form.perms.entries.append(perm_field)
        a += 1
    return form


def generate_command_field(cogs):

    form = CommandsForm()
    a = 0
    b = 0
    for cog in sorted(cogs):
        commands = cogs[cog]
        commands.sort(key=lambda x: x[0])
        cog_form = CogField()

        for command in commands:
            command_field = CommandField()

            command_field.check.label = command[0]
            command_field.check.data = command[1]

            command_field.check.name = f'command-{b}-{command[0]}'
            command_field.desc = command[2]
            cog_form.commands.entries.append(command_field)
            b += 1
        cog_form.label = cog.title()
        cog_form.commands.name = f'cog-{a}-{cog}'
        form.cogs.entries.append(cog_form)
        a += 1
    return form

    return form
