
from collections import namedtuple
import panel as pn
from tempfile import NamedTemporaryFile
from pathlib import Path
import xarray as xr

from swarmpal.io import PalDataItem, create_paldata

from common import HEADER, JINJA2_ENVIRONMENT

pn.extension('filedropper')
xr.set_options(display_expand_groups=True, display_expand_attrs=True, display_expand_data_vars=True, display_expand_coords=True)


class DataExplorer:
    def __init__(self):
        self.file_dropper = pn.widgets.FileDropper(multiple=False)
        self.data_view = pn.pane.HTML()
        self.file_dropper.param.watch(self.update_data_view, 'value')

    @property
    def temp_file(self):
        """Access the stored temporary file"""
        return self._temp_file

    def update_temp_file(self):
        """Write a temporary file to disk so that SwarmPAL CDF reader can read it."""
        if self.file_dropper.value:
            self._temp_file = NamedTemporaryFile(
                prefix=Path(self.file_in_mem.name).stem,
                suffix=Path(self.file_in_mem.name).suffix,
            )
            with open(self._temp_file.name, 'wb') as f:
                f.write(self.file_in_mem.content)
        else:
            self._temp_file = None
    
    @property
    def file_in_mem(self):
        """Accessed as: file_in_mem.name and file_in_mem.content"""
        file_name, file_content = next(iter(self.file_dropper.value.items()))
        File = namedtuple('File', ['name', 'content'])
        file = File(file_name, file_content)
        return file

    
    @property
    def swarmpal_data(self):
        """Accesses the data in the temporary file as a SwarmPAL DataTree"""
        if self.temp_file:
            product_name = Path(self.file_in_mem.name).stem
            return create_paldata(
                **{product_name: PalDataItem.from_file(self.temp_file.name, filetype="cdf")},
            )
        else:
            return None
    
    @property
    def swarmpal_data_view(self):
        if self.swarmpal_data:
            return self.swarmpal_data._repr_html_()
        else:
            return "No data available."

    def update_data_view(self, event):
        self.update_temp_file()
        if self.file_dropper.value:
            self.data_view.object = self.swarmpal_data_view
        else:
            self.data_view.object = "No file uploaded / unsupported data format."


data_explorer = DataExplorer()
dashboard = pn.template.BootstrapTemplate(
    header=HEADER,
    title="SwarmPAL CDF file viewer",
    main=pn.Column(
        data_explorer.file_dropper,
        data_explorer.data_view,
    )
).servable()


if __name__ == "__main__":
    dashboard.show()
