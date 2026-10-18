"""Generate the WRR submission cover letter as cover_letter.docx."""
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\cover_letter.docx"

doc = docx.Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)

def para(text, bold_lead=None, space_after=12):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
    p.add_run(text)
    return p

# Date and address block
para("October 18, 2026")
para("Editors-in-Chief\nWater Resources Research\nAmerican Geophysical Union")

para("Dear Editors,")

para(
    'we are pleased to submit our manuscript entitled "When Catchment Response Itself Drifts: '
    'Decomposing Time-Varying Hydrologic Sensitivity and Memory Across 2,146 Near-Natural '
    'Catchments" for consideration as an original research article in Water Resources Research.',
)

para(
    "Streamflow attribution and projection studies almost universally assume that the catchment "
    "response function—climate elasticity, sensitivity, and memory—is stationary in time, even though "
    "the meteorological forcing itself is changing. Whether the response function drifts, and what such "
    "drift would do to attribution, has remained unresolved. Our manuscript addresses this gap directly.",
)

para(
    "Using daily streamflow from 2,146 near-natural catchments spanning all continents and daily "
    "ERA5-Land forcing, we estimate time-varying sensitivity and memory with distributed-lag models in "
    "rolling 15-year windows, and decompose each parameter trajectory into (i) a composition component "
    "explained by concurrent forcing-distribution changes and (ii) a residual component. We find that "
    "residual drift contributes 37\u201347% of total parameter variation, is climate-structured "
    "(sensitivity drift dominates in water-limited catchments; memory drift in snow-influenced and arid "
    "catchments), and is spatially coherent well beyond estimation noise (Moran's I = 0.06\u20130.32, "
    "all p < 0.05). Critically, freezing the response function at its earliest-window level alters the "
    "attributed climate contribution by more than 10% in 80% of catchments.",
)

para(
    "We believe this work fits the scope of Water Resources Research particularly well: it couples a "
    "methodological advance (a decomposition framework separating forced composition from residual "
    "drift) with a large-sample, management-relevant diagnosis (when and where non-stationary response "
    "changes the numbers that water managers actually use). The results imply that routine "
    "re-estimation of response functions should become part of attribution practice, and provide a "
    "quantitative basis for deciding when the stationarity assumption is defensible.",
)

para(
    "This manuscript is original, has not been published previously, and is not under consideration "
    "by any other journal. All authors have read and approved the submitted version and declare no "
    "competing interests. All datasets used are publicly available (seven streamflow collections "
    "including ROBIN, GRDC-Caravan, USGS NWIS, HIDROWEB, Datos de Caudales, GSIM, and the Chinese "
    "Hydrological Yearbook; ERA5-Land meteorological forcing), and the analysis scripts that reproduce "
    "every figure and table will be archived upon acceptance.",
)

para(
    "Thank you for considering our submission. We look forward to the reviewers' comments and would be "
    "glad to provide any further information."
)

para("Sincerely,")
para("[Corresponding Author Name]")
para("[Affiliation]")
para("[Email Address]")

doc.save(OUT)
print("Cover letter saved to", OUT)
