import ast
import pandas as pd
import unidecode

from os import getcwd, path, stat
from datetime import datetime


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
    style: [string] Representation of the style of the training set.

    Returns
    -------
    True: if style is in log
    False: if style is not in log
    """
    with open(path.join(DATAPATH, 'changelog.txt'), 'r') as f:
        log = f.readlines()

        # Check if style was a.readlines()y exported
        if is_substring(style, log):
            return True
        else:
            return False


def create_dataset(csv, prompt=None, completion=None, target_path=None):
    """
    Takes a CSV and creates a dataset with the arguments passed

    Parameters
    ----------
    csv: [string] Path of CSV file.
    prompt: [string] Column(s) that will be GPT-3's prompt.
    completion: [string] Column that will be GPT-3's completion.

    Returns
    -------
    Nothing

    Yields
    ------
    JSON Lines file with the prompt and completion
    """
    df = pd.read_csv(csv)
    timestamp = datetime.now().strftime('%Y%m%d%H%M')

    # get target path
    if target_path == None:
        target_path = DATAPATH

    # Subset dataframe
    if type(prompt) == list:
        # Initialize completion column with first prompt
        df['prompt'] = promptize(df, prompt[0])
        prompt_name = []

        # Join subsequent prompts
        for col in prompt[1:]:            
            df['prompt'] = df['prompt'] + promptize(df, col)
            prompt_name.append(col[0])

        # Add the final separator
        df['prompt'] = df['prompt'] + '\n\n###\n\n'
        prompt_name = ''.join(prompt_name) + completion[0:4]
    else:
        df['prompt'] = df[prompt] + '\n\n###\n\n'
        prompt_name = prompt[0:4] + completion[0:4]

    train = df.loc[:,['prompt', completion]]
    train = train.rename(columns={completion:'completion'})
    filename = prompt_name + timestamp + '.jsonl'
    filepath = path.join(target_path, filename)
    return train.to_json(filepath, orient='records', lines=True)


# Main functions
def convert(csv, style=None, target_path=None):
    """
    Converts CSV file to JSON Lines format
    
    Parameters
    ----------
    csv: [string] Path of the input CSV file.
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
        return create_dataset(csv, prompt='features', completion='product')
    elif style == 'feat-head':
        return create_dataset(csv, prompt='features', completion='headline')
    elif style == 'prod-head':
        return create_dataset(csv, prompt='product', completion='headline')
    else:
        raise ValueError('\U0001F635 The value you chose is invalid')


if __name__ == '__main__':
    changes = which_changed()
    choice = input("Choose style (feat-prod, feat-head or prod-head): ")
    if not in_log(choice) or changes == 'both':
        if choice not in ['feat-prod', 'feat-head', 'prod-head']:
            raise ValueError("\U0001F635 The value you chose is invalid.\n")
        else:
            csv = path.join(DATAPATH, 'db.csv')
            convert(csv=csv, style=choice)

            # log changes
            with open(path.join(DATAPATH, 'changelog.txt'), 'r') as f:
                log = [item.replace('\n', '') for item in f.readlines()]

            if is_substring('exports', log):
                exports = [
                    ', '.join([item, choice]) for item in log if 'exports' in item][0]
            else:
                exports = 'exports: ' + choice
            
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
