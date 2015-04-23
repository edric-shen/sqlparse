# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

"""Parse SQL statements."""


__version__ = '0.1.14'


# Setup namespace
from sqlparse import engine
from sqlparse import filters
from sqlparse import formatter
from sqlparse import lexer
from sqlparse.engine import grouping

# Deprecated in 0.1.5. Will be removed in 0.2.0
from sqlparse.exceptions import SQLParseError


def parse(
    sql,
    encoding=None,
    pre_processes=None,
    stmt_processes=None,
    post_processes=None,
    grouping_funcs=None
):
    """Parse sql and return a list of statements.

    :param sql: A string containting one or more SQL statements.
    :param encoding: The encoding of the statement (optional).
    :param pre_processes: pre_processes you want to run against parsed statements (optional).
    :param stmt_processes: stmt_processes you want to run against parsed statements (optional).
    :param post_processes: post_processes you want to run against parsed statements (optional).
    :param grouping_funcs: grouping_funcs you want to run against parsed statements (optional).
    :returns: A tuple of :class:`~sqlparse.sql.Statement` instances.
    """
    stream = parse_stream(
        sql,
        encoding,
        pre_processes=pre_processes or [],
        stmt_processes=stmt_processes or [],
        post_processes=post_processes or [],
        grouping_funcs=grouping_funcs or []
    )
    # for statement in stream:
    #     if statement.get_type() == 'CREATE':

    return tuple(stream)


def parse_stream(
    stream,
    encoding=None,
    pre_processes=None,
    stmt_processes=None,
    post_processes=None,
    grouping_funcs=None
):
    """Parses sql statements from file-like object.

    :param stream: A file-like object.
    :param encoding: The encoding of the stream contents (optional).
    :param pre_processes: pre_processes you want to run against parsed statements (optional).
    :param stmt_processes: stmt_processes you want to run against parsed statements (optional).
    :param post_processes: post_processes you want to run against parsed statements (optional).
    :param grouping_funcs: grouping_funcs you want to run against parsed statements (optional).
    :returns: A generator of :class:`~sqlparse.sql.Statement` instances.
    """
    stack = engine.FilterStack(
        pre_processes=pre_processes or [],
        stmt_processes=stmt_processes or [],
        post_processes=post_processes or []
    )
    stack.full_analyze()
    if grouping_funcs:
        stack.grouping_funcs = grouping_funcs
    return stack.run(stream, encoding)


def format(sql, **options):
    """Format *sql* according to *options*.

    Available options are documented in :ref:`formatting`.

    In addition to the formatting options this function accepts the
    keyword "encoding" which determines the encoding of the statement.

    :returns: The formatted SQL statement as string.
    """
    encoding = options.pop('encoding', None)
    stack = engine.FilterStack()
    options = formatter.validate_options(options)
    stack = formatter.build_filter_stack(stack, options)
    stack.post_processes.append(filters.SerializerUnicode())
    return ''.join(stack.run(sql, encoding))


def split(sql, encoding=None):
    """Split *sql* into single statements.

    :param sql: A string containting one or more SQL statements.
    :param encoding: The encoding of the statement (optional).
    :returns: A list of strings.
    """
    stack = engine.FilterStack()
    stack.split_statements = True
    return [unicode(stmt).strip() for stmt in stack.run(sql, encoding)]


from sqlparse.engine.filter import StatementFilter


def split2(stream):
    splitter = StatementFilter()
    return list(splitter.process(None, stream))
