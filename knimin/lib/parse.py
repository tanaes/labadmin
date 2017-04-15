# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The LabAdmin Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from StringIO import StringIO

import pandas as pd
import numpy as np


def parse_plate_reader_output(contents):
    """Parses the output of a plate reader
    The format supported here is a tab delimited file in which the first line
    contains the fitting curve followed by (n) blank lines and then a tab
    delimited matrix with the values

    Parameters
    ----------
    contents : str
        The contents of the plate reader output

    Returns
    -------
    np.array of floats
        A 2D array of floats
    """
    data = []
    for line in contents.splitlines():
        line = line.strip()
        if not line or line.startswith('Curve'):
            continue
        data.append(line.split())

    return np.asarray(data, dtype=np.float)


def parse_qpcr_object(contents):
    """ Parses a QPCR machine string, returning the per well Cps

    Parameters
    ----------
    contents : str
        The string generated by the QPCR machine to parse.
        New lines \n, field \t

    Returns
    -------
    numpy.array 2D
        The per well concentrations

    Raises
    ------
        ValueError
            If Cp or Pos is not one of the headers
    """
    contents = pd.read_csv(
            StringIO(contents),
            sep='\t',
            dtype=str,
            encoding='utf-8',
            infer_datetime_format=False,
            keep_default_na=False,
            index_col=False,
            comment='\t')

    headers = contents.columns.values
    if 'Cp' not in headers or 'Pos' not in headers:
        raise ValueError("The 'Cp' and 'Pos' headers are "
                         "required. The ones present are: %s" % headers)

    # Pos format is A1 -> [0][0], B24 -> [1][23], etc so the max row will
    # be the first letter - 'A' + 1
    max_row = sorted(contents.Pos.values,
                     key=lambda item: item[0])[-1][0]
    max_row = ord(max_row) - ord('A') + 1
    # the max columns is the max number after the letter - 1
    max_col = sorted(contents.Pos.values,
                     key=lambda item: int(item[1:]))[-1][1:]
    max_col = int(max_col)

    result = np.empty((max_row, max_col))
    result[:] = np.nan

    for idx, row in contents.iterrows():
        # if Cp is empty default to nan
        value = float(row.Cp) if row.Cp != '' else np.nan
        r = ord(row.Pos[0]) - ord('A')
        c = int(row.Pos[1:]) - 1
        result[r, c] = value

    return result
