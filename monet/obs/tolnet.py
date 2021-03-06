import os
from builtins import object

import pandas as pd
import xarray as xr


class TOLNet(object):
    def __init__(self):
        self.objtype = 'TOLNET'
        self.cwd = os.getcwd()
        self.dates = pd.date_range(start='2017-09-25', end='2017-09-26', freq='H')
        self.dset = None

    def open_data(self, fname):
        from h5py import File
        f = File(fname)
        atts = f['INSTRUMENT_ATTRIBUTES']
        data = f['DATA']
        self.dset = self.make_xarray_dataset(data, atts)

    @staticmethod
    def make_xarray_dataset(data, atts):
        from numpy import NaN
        # altitude variables
        alt = data['ALT'][:].squeeze()
        altvars = ['AirND', 'AirNDUncert', 'ChRange', 'Press', 'Temp', 'TempUncert', 'O3NDResol', 'PressUncert']
        # time variables
        tseries = pd.Series(data["TIME_MID_UT_UNIX"][:].squeeze())
        time = pd.Series(pd.to_datetime(tseries, unit='ms'), name='time')
        tseries = pd.Series(data["TIME_START_UT_UNIX"][:].squeeze())
        stime = pd.to_datetime(tseries, unit='ms')
        tseries = pd.Series(data["TIME_STOP_UT_UNIX"][:].squeeze())
        etime = pd.to_datetime(tseries, unit='ms')
        # all other variables
        ovars = ['O3MR', 'O3ND', 'O3NDUncert', 'O3MRUncert', 'Precision']
        dset = {}
        for i in ovars:
            val = data[i][:]
            val[data[i][:] < -999.] = NaN
            dset[i] = (['z', 't'], val)
        for i in altvars:
            dset[i] = (['z'], data[i][:].squeeze())
        # coords = {'time': time, 'z': alt, 'start_time': stime, 'end_time': etime}
        attributes = {}
        for i in list(atts.attrs.keys()):
            attributes[i] = atts.attrs[i]
        dataset = xr.Dataset(data_vars=dset, attrs=attributes)
        dataset['time'] = (['t'], time)
        dataset['t'] = dataset['time']
        dataset = dataset.drop('time').rename({'t': 'time'})
        dataset['z'] = alt
        dataset.attrs['Latitude'] = float(dataset.Location_Latitude.split(' ')[0])
        dataset.attrs['Longitude'] = -1. * float(dataset.Location_Longitude.split(' ')[0])
        return dataset
