import ast
import pandas as pd
import unidecode

from os import getcwd, path, stat
from datetime import datetime
from numpy import mean, floor


# constants
DATAPATH = path.join(getcwd(), 'data')
NUM = str(stat(path.join(DATAPATH, 'db.numbers')))
CSV = str(stat(path.join(DATAPATH, 'db.csv')))


# Helper functions
def promptize(df, col_name):
    """
    Prepare a column in a list to become a part in a prompt

    Parameters
    ----------
    df: [pandas.DataFrame] Dataframe that contains the column
    col_name: [string] Name of the column

    Returns
    -------
    pandas.Series with the modified prompt
    """
    text = df[col_name].apply(lambda x: unidecode.unidecode(x))
    return col_name + ': ' + text + '\n'


def name_style(prompts, completion):
    """
    Give name to the data set style given a string or a list
    
    Paramaters
    ----------
    prompts: [string or list] Representation of the inputs used
    completion: [string] Representation of the output

    Returns
    -------
    Style string.
    """
    if type(prompts) == list:
        return ''.join(
            [string[0:4] for string in prompts]) + '-' + completion[0:4]
    elif type(prompts) == str:
        return prompts[0:4] + '-' + completion[0:4]
    else:
        raise ValueError(
            "The prompt you provided should be a list or a string")


def which_changed():
    """
    Verify the changes made to the databases

    Parameters
    ----------
    None

    Returns
    -------
    'csv': if the CSV file has changed.
    'num': if the numbers file has changed.
    'both': if both files have changed.
    'neither': if both files haven't changed.
    """
    # get stats
    with open(path.join(DATAPATH, 'changelog.txt'), 'r') as f:
        log = f.readlines()

    log = [x.replace('\n', '') for x in log]

    # Check which files have changed.
    # If changed, they're not on the list.
    if NUM in log and CSV not in log:
        res = 'csv'
    elif NUM in log and CSV in log:
        res = 'neither'
    elif NUM not in log and CSV in log:
        res = 'num'
    elif NUM not in log and CSV not in log:
        res = 'both'
    
    return res


def is_substring(string, target):
    """
    Checks if a string is a subset of a larger string in a list
    
    Parameters
    ----------
    string: [string] The string that is being searched in the list.
    target: [list] The target list in which the string is being searched.

    Returns
    -------
    True: if string is a substring of an element in a list
    False: if string is not a substring of an element in a list
    """
    return bool(sum([True for item in target if string in item]))


def in_log(style):
    """
    Records the style in changelog to allow creating different training
    sets.

    Parameters
    ----------
    style: [string or list] Representation of the style of the training set.

    Returns
    -------
    True: if style is in log
    False: if style is not in log
    """
    with open(path.join(DATAPATH, 'changelog.txt'), 'r') as f:
        log = f.readlines()

        # Check if style was exported already
        if type(style) == list:
            return bool(floor(mean([is_substring(string, log)])))
        else:
            return is_substring(style, log)


def create_dataset(df, prompt=None, completion=None, target_path=None):
    """
    Takes a CSV and creates a dataset with the arguments passed

    Parameters
    ----------
    df: [pandas.DataFrame] Data frame containing the database.
    prompt: [string or list] Column(s) that will be GPT-3's prompt.
    completion: [string] Column that will be GPT-3's completion.

    Returns
    -------
    Nothing

    Yields
    ------
    JSON Lines file with the prompt and completion
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M')

    # get target path
    if target_path == None:
        target_path = DATAPATH

    # Subset dataframe
    if type(prompt) == list:
        # Initialize completion column with first prompt
        df['prompt'] = promptize(df, prompt[0])

        # Join subsequent prompts
        for col in prompt[1:]:            
            df['prompt'] = df['prompt'] + promptize(df, col)

        # Add the final separator
        df['prompt'] = df['prompt'] + '\n\n###\n\n'
    else:
        df['prompt'] = df[prompt] + '\n\n###\n\n'

    train = df.loc[:,['prompt', completion]]
    train = train.rename(columns={completion:'completion'})
    filename = name_style(prompt, completion) + timestamp + '.jsonl'
    filepath = path.join(target_path, filename)

    return train.to_json(filepath, orient='records', lines=True)


# Main functions
def convert(df, style=None, target_path=None):
    """
    Converts CSV file to JSON Lines format
    
    Parameters
    ----------
    df: [pandas.DataFrame] Data frame containing the database
    style: [string] Indicates the type of training dataset that will be
           converted into. Available options are:
           'feat-prod': From feature specifications to product description.
           'feat-head': From features specifications to headline.
           'prod-head': From product description to headline.

    Returns:
    --------
    Nothing

    Yields
    ------
    JSON Line file according to parameter specification.
    """    
    # export the right training set
    if style == 'feat-prod':
        return create_dataset(df, prompt='features', completion='product')
    elif style == 'feat-head':
        return create_dataset(df, prompt='features', completion='headline')
    elif style == 'prod-head':
        return create_dataset(df, prompt='product', completion='headline')
    else:
        raise ValueError('\U0001F635 The value you chose is invalid')


if __name__ == '__main__':
    changes = which_changed()
    df = pd.read_csv(path.join(DATAPATH, 'db.csv'))
    available = ', '.join([col for col in df.columns])

    prompt = input("Choose prompts. Available choices: " + available + ': ')
    prompt = prompt.split(', ')
    completion = input("Choose compeltion: ")

    # Check that choices are valid
    if not set(prompt).issubset(df.columns):
        raise ValueError("\U0001F635 The value you chose is invalid.\n")

    if len(prompt) == 1:
        prompt = prompt[0]

    if not in_log(name_style(prompt, completion)) or changes == 'both':
            create_dataset(df, prompt=prompt, completion=completion)

            # log changes
            with open(path.join(DATAPATH, 'changelog.txt'), 'r') as f:
                log = [item.replace('\n', '') for item in f.readlines()]

            if is_substring('exports', log):
                exports = [
                    ', '.join([item, name_style(prompt, completion)]) for item in log if 'exports' in item][0]
            else:
                exports = 'exports: ' + name_style(prompt, completion)
            
            # Erase file
            open(path.join(DATAPATH, 'changelog.txt')).close()

            with open(path.join(DATAPATH, 'changelog.txt'), 'w') as f:
                f.write('\n'.join([NUM, CSV, exports]))

            print("\n\U0001F91C \U0001F91B Yesss. You did it, champ.\n")
    elif in_log and changes == 'neither':
        print("\n\U0001F996 You already exported this, bro.\n")
    else:
        print(
            "\n\U0001F921 LOL, something is wrong. Only {} changed.\n".format(
            changes))
