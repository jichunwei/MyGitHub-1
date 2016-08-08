'''
*** The Messages.py is the implementation of ConfigObj, is a powerful and
flexible configuration file parser suitable for any configuration needs. ***

Why we use ConfigObj instead of Python standard library ConfigParser?

The biggest advantage of ConfigObj is simplicity. Even for trivial configuration
files, where you just need a few key value pairs, ConfigParser requires them
to be inside a 'section'. ConfigObj doesn't have this restriction, and having
read a config file into memory, accessing members is trivially easy.

Let's look at a simple example. Given a filename pointing to a configuration
file containing these members:

name = Michael Foord
# this comment belongs to 'DOB'
DOB = 12th August 1974 # an inline comment
nationality = English

We access it with the following snippet of code. After initializing a ConfigObj
instance with a filename, you can then access members using dictionary like
syntax:
>>> from configobj import ConfigObj
>>> config = ConfigObj('config.ini')
>>> config['name']
'Michael Foord'
>>> config['DOB']
'12th August 1974'
>>> config['nationality']
'English'

Beyond simplicity, ConfigObj has some more important advantages over ConfigParser.
These include:
    * Unicode support
    * List values
    * Multi-line values
    * Nested sections (subsections) to any depth
    * When writing out config files, ConfigObj preserves all comments and the
      order of members and sections
    * Many useful methods and options for working with configuration files
      (like the merge() and reload() methods)
    * An unrepr mode for persisting Python basic types
    * An integrated validation and type conversion system. This allows you to
      check the validity of configuration files and supply default values.

Some of these you can take advantage of without having to do anything special
in your own code. Particularly useful are multi-line values (with familiar
triple quotes) and comma separated list values. Let's expand our simple
config file with a couple of new members:

description = """
A hairy individual.
But with many redeeming features."""

attributes = 2 arms, 2 legs, "nose, slightly large"

When we access these members programmatically they become:
>>> config['description']
'\nA hairy individual.\nBut with many redeeming features.'
>>> config['attributes']
['2 arms', '2 legs', 'nose, slightly large']

Of course ConfigObj does allow you to use sections and exposes them using the
dictionary access idiom.


*** The Config File Format ***
---------------------------------------------------------------------------
# initial comment
keyword1 = value1
keyword2 = value2

[section 1]
keyword1 = value1
keyword2 = value2

    [[sub-section]]
    # this is in section 1
    keyword1 = value1
    keyword2 = value2

        [[[nested section]]]
        # this is in sub section
        keyword1 = value1
        keyword2 = value2

    [[sub-section2]]
    # this is in section 1 again
    keyword1 = value1
    keyword2 = value2

[[sub-section3]]
# this is also in section 1, indentation is misleading here
keyword1 = value1
keyword2 = value2

# final comment

---------------------------------------------------------------------------

When parsed, the above config file produces the following data structure:

ConfigObj({
    'keyword1': 'value1',
    'keyword2': 'value2',
    'section 1': {
        'keyword1': 'value1',
        'keyword2': 'value2',
        'sub-section': {
            'keyword1': 'value1',
            'keyword2': 'value2',
            'nested section': {
                'keyword1': 'value1',
                'keyword2': 'value2',
            },
        },
        'sub-section2': {
            'keyword1': 'value1',
            'keyword2': 'value2',
        },
        'sub-section3': {
            'keyword1': 'value1',
            'keyword2': 'value2',
        },
    },
})


NOTES:
The code requires the Python package configobj installed.
Source: http://pypi.python.org/pypi/configobj/
'''
import logging

from configobj import ConfigObj
from StringIO import StringIO

_txt_rep = (
    # in 9.0, NOT conformed to ConfigObj spec
    ("='", "=&'"),
    # duplicated keys (in /bin/messages or /bin/messages.en_US)
    ("Location=Location", "#Location=Location"), 
    ("CF_WlanUsage=", "#CF_WlanUsage="),
    ("MSG_AP_gen_RFInfo=", "#MSG_AP_gen_RFInfo="),
)

_const = dict (
    zd_msg_file = '/bin/messages',
    fm_msg_file = '',
    ap_msg_file = '',
)

_config_opt = dict (
    list_values = False,
)

class Messages(object):
    _messages = {}

    @classmethod
    def get_messages(cls):
        '''
        Returns a dict containing bundled messages of zd, fm and ap
        '''
        return cls._messages


    @classmethod
    def load_zd_messages(cls, zd_cli, msg_file = _const['zd_msg_file']):
        '''
        Loads the messages bundled from ZoneDirector CLI

        @param zd_cli:
            An instance of ZoneDirectorCLI
        @param msg_file:
            Location of the bundled messages

        @return:
            A ConfigObj object.
        '''

        logging.debug('Getting bundled messages at %s' % msg_file)
        messages = zd_cli.do_shell_cmd('cat %s' % msg_file, timeout = 20, print_message = False)

        logging.debug('Parsing messages...')
        try:
            parsed_msg = cls._parse_messages(messages)

        except Exception, e:
            logging.debug(e.message)

        if not cls._messages.has_key('zd'):
            cls._messages['zd'] = parsed_msg

        else:
            cls._messages['zd'].update(parsed_msg)


        return cls.get_messages()['zd']


    @classmethod
    def _parse_messages(cls, messages):
        '''
        A configuration file parser that deals with key-value pairing

        @param messages:
            A string that its structure is similar to what you would find on
            Microsoft Windows INI files
        @return:
            A ConfigObj object.
        '''

        # refines the source messages to conform to ConfigObj structure
        for t in _txt_rep:
            messages = messages.replace(t[0], t[1])

        # turns the above messages string into a file-like object,
        # which ConfigObj is expecting
        fh = StringIO(messages)

        parser = ConfigObj(fh, **_config_opt)

        return parser

