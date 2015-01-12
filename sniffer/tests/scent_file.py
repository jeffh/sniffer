from sniffer.api import *


@select_runnable('execute_type1')
@file_validator
def type1_files(filename):
    return filename.endswith('.type1')


@select_runnable('execute_type2')
@file_validator
def type2_files(filename):
    return filename.endswith('.type2')


@runnable
def execute_type1(mock, *args):
    mock('type1')


@runnable
def execute_type2(mock, *args):
    mock('type2')
