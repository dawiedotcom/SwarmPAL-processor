# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: swarmpal-processor
#     language: python
#     name: swarmpal-processor
# ---

# %%
import random
import string
import datetime as dt
import panel as pn
import hvplot.xarray
from tempfile import NamedTemporaryFile
import shutil
import os

from swarmpal.express import fac_single_sat

# %%
pn.extension()

# %%
start_of_today = dt.datetime.now().date()
end_of_today = start_of_today + dt.timedelta(days=1)
four_weeks_ago = end_of_today - dt.timedelta(days=28)

widgets = {
        "spacecraft": pn.widgets.RadioBoxGroup(options=["Swarm-A", "Swarm-B", "Swarm-C"]),
        "grade": pn.widgets.RadioBoxGroup(options=["OPER", "FAST"], value="FAST"),
        "start-end": pn.widgets.DatetimeRangePicker(
            start=four_weeks_ago,
            end=end_of_today,
            value=(start_of_today, end_of_today),
            enable_time=False,
        ),
        "action-button": pn.widgets.Button(name="Evaluate", button_type="primary")
    }

controls = pn.Column(
    widgets["start-end"],
    widgets["spacecraft"],
    widgets["grade"],
    widgets["action-button"],
)
controls


# %%
class FacDataExplorer:
    def __init__(self, widgets):
        self.widgets = widgets
        self.cdf_download = pn.widgets.FileDownload(button_type="success")
        self.output_pane = pn.Column(
            pn.pane.Markdown(),
            pn.pane.HoloViews(),
            pn.layout.Divider(),
            self.cdf_download,
        )
        self.widgets["action-button"].on_click(self.update_data)
        self.update_data(None)

    @property
    def controls(self):
        return pn.Column(
            self.widgets["start-end"],
            self.widgets["spacecraft"],
            self.widgets["grade"],
            self.widgets["action-button"],
        )

    @property
    def time_start_end_str(self):
        t_s, t_e = self.widgets["start-end"].value
        return f'{t_s.strftime("%Y%m%dT%H%M%S")}_{t_e.strftime("%Y%m%dT%H%M%S")}'

    @property
    def spacecraft(self):
        return self.widgets["spacecraft"].value

    @property
    def grade(self):
        return self.widgets["grade"].value

    def update_data(self, event):
        self.data = fac_single_sat(
            spacecraft=self.widgets["spacecraft"].value,
            grade=self.widgets["grade"].value,
            time_start=self.widgets["start-end"].value[0].isoformat(),
            time_end=self.widgets["start-end"].value[1].isoformat(),
        )
        self._update_output_pane()
        self._update_cdf_file()

    def _update_output_pane(self):
        title = f'## {self.widgets["spacecraft"].value} {self.widgets["grade"].value}\n{self.widgets["start-end"].value[0]} to {self.widgets["start-end"].value[1]}'
        mask_valid_F = self.data["PAL_FAC_single_sat"]["Flags_F"] <= 1
        mask_valid_B = self.data["PAL_FAC_single_sat"]["Flags_B"] <= 1
        mask_valid = mask_valid_F & mask_valid_B
        masked_data = self.data["PAL_FAC_single_sat"].to_dataset().where(mask_valid, drop=True)
        hvplot_obj = masked_data.hvplot(x="Timestamp", y="FAC", ylim=(-30, 30))
        # hvplot_obj = self.data["PAL_FAC_single_sat"].to_dataset().hvplot(x="Timestamp", y="FAC", ylim=(-30, 30))
        self.output_pane[0].object = title
        self.output_pane[1].object = hvplot_obj

    def get_cdf_file(self):
        # work around the weirdness of cdflib xarray tools by writing to another file first then moving to a temporary file
        deleteme ="/tmp/tmp" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + ".cdf"
        self.data.swarmpal.to_cdf(deleteme, leaf="PAL_FAC_single_sat")
        # Create the tempfile as a an object property so it doesn't go out of scope and get deleted
        # It will automatically be replaced (and old file removed) each time this is run
        self.tempfile_cdf = NamedTemporaryFile()
        with open(deleteme, "rb") as src_file:
            shutil.copyfileobj(src_file, self.tempfile_cdf)
            self.tempfile_cdf.seek(0)
        os.remove(deleteme)
        return self.tempfile_cdf

    def _update_cdf_file(self):
        self.cdf_download.file = self.get_cdf_file().name
        self.cdf_download.filename = f'SwarmPAL_FAC_{self.spacecraft}_{self.grade}_{self.time_start_end_str}.cdf'


data_explorer = FacDataExplorer(widgets)

# %%
data_explorer.output_pane

# %%
dashboard = pn.template.BootstrapTemplate(
    title="SwarmPAL dashboard: FAC",
    sidebar=data_explorer.controls,
    main=data_explorer.output_pane,
)
if "get_ipython" in globals():
    dashboard.show()
else:
    dashboard.servable()
