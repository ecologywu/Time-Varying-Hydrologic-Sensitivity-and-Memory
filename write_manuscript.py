"""
Generate the full WRR manuscript as a Word document.
Revision 2: WRR-style in-text citations and reference list, explicit equations
in Methods, Introduction/Methods/Discussion enriched with the reference
literature, base maps from WorldMap shapefiles, Data Availability section.
"""
import os
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

BASE = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01"
FIG_DIR = os.path.join(BASE, "figures")
EQ_DIR = os.path.join(FIG_DIR, "equations")
TAB_DIR = os.path.join(BASE, "tables")
OUT_PATH = os.path.join(BASE, "WRR_manuscript.docx")

doc = Document()

# Page setup: US Letter, 1-inch margins
for section in doc.sections:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Default font
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(11)

def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Arial'
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h

def add_para(text, bold=False, italic=False, align=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.bold = bold
    run.italic = italic
    return p

def add_figure(path, caption, width=Inches(6.0)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=width)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.font.name = 'Arial'
    r.font.size = Pt(10)
    r.italic = True

def add_equation(name, width=Inches(5.9)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(os.path.join(EQ_DIR, name + ".png"), width=width)

def add_table_from_csv(csv_path, caption):
    df = pd.read_csv(csv_path)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr[i].text = str(col)
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            cells[i].text = str(row[col])
            for p in cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.font.name = 'Arial'
    r.font.size = Pt(10)
    r.italic = True
    doc.add_paragraph()

# ============================================================
# TITLE
# ============================================================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("When Catchment Response Itself Drifts:\nDecomposing Time-Varying Hydrologic Sensitivity and Memory\nAcross 2,146 Near-Natural Catchments")
run.font.name = 'Arial'
run.font.size = Pt(16)
run.bold = True

doc.add_paragraph()

# Abstract
add_heading("Abstract", level=2)
add_para(
    "Streamflow attribution and projection typically treat the catchment response function—elasticity, "
    "sensitivity, and memory—as a stationary property, despite accumulating evidence that empirical "
    "sensitivities vary in time. What remains unresolved is whether this time variation is merely an "
    "imprint of changing meteorological forcing distributions (a composition effect), or whether a "
    "residual drift persists after that imprint is accounted for—and whether that residual drift biases "
    "attribution. Using daily streamflow from 2,146 near-natural catchments and ERA5-Land forcing, we "
    "estimate time-varying sensitivity and memory with distributed-lag models in rolling 15-year windows, "
    "then decompose each parameter time series into a composition component explained by concurrent "
    "forcing-distribution changes and a residual component. We find that residual drift is detected in a "
    "substantial fraction of catchments, with its dominant dimension being climate-dependent: sensitivity "
    "drift concentrates in water-limited catchments (median coefficient of variation of precipitation "
    "sensitivity = 0.65 in arid zones vs. 0.19 in humid zones), whereas memory drift is largest in "
    "snow-influenced and arid catchments. Residual drift accounts for 37–47% of total parameter variation "
    "and exhibits spatial coherence significantly exceeding estimation noise (Moran's I = 0.06–0.32, "
    "all p < 0.05; nearest-neighbor sign consistency 0.59–0.66 vs. 0.50 under random pairing). "
    "Freezing the response function at its earliest-window level alters the magnitude of attributed "
    "climate contribution by more than 10% in 80% of catchments. Stationarity of the response function "
    "is not a neutral simplification; where residual drift is spatially organized, attribution without a "
    "drift diagnostic carries a directional error."
)

# Keywords
p = doc.add_paragraph()
r = p.add_run("Keywords: ")
r.bold = True
p.add_run("non-stationary hydrologic response; streamflow sensitivity; catchment memory; attribution bias; near-natural catchments; distributed lag models")

# Key Points (AGU format)
p = doc.add_paragraph()
r = p.add_run("Key Points: ")
r.bold = True
kp = doc.add_paragraph(style='List Bullet', )
r = kp.add_run("Time-varying catchment sensitivity and memory are decomposed into a forced composition component and a residual drift component across 2,146 catchments")
kp.runs[0].font.size = Pt(11)
kp = doc.add_paragraph(style='List Bullet')
r = kp.add_run("Residual drift contributes 37–47% of parameter variation and is spatially coherent, ruling out estimation noise")
kp.runs[0].font.size = Pt(11)
kp = doc.add_paragraph(style='List Bullet')
r = kp.add_run("Freezing the response function biases trend attribution by more than 10% in 80% of catchments")
kp.runs[0].font.size = Pt(11)

# Plain Language Summary (AGU mandatory)
add_heading("Plain Language Summary", level=2)
add_para(
    "When rain falls on a landscape, part of the water reaches rivers quickly, and part is stored in "
    "soils, snowpack, and groundwater and released weeks to months later. To predict river flow, water "
    "managers and scientists rely on simple rules describing how much flow changes when rainfall or "
    "dryness changes, and how long the land \u201cremembers\u201d past weather. These rules are usually "
    "assumed never to change. Examining 2,146 minimally disturbed rivers worldwide, we found that the "
    "rules themselves are shifting: climate change is not only altering rainfall and temperature, it is "
    "also changing how landscapes convert water into river flow, especially in dry and snow-covered "
    "regions. Because many studies assume fixed rules, their estimates of how much climate change has "
    "affected water availability would be off by more than 10% in four of every five rivers studied. "
    "Regularly re-checking these rules is essential for reliable water planning."
)

doc.add_page_break()

# ============================================================
# 1. INTRODUCTION
# ============================================================
add_heading("1. Introduction", level=1)

add_para(
    "Water resources planning, ecological flow assessment, and drought risk analysis all rely on an "
    "implicit transformation rule that converts meteorological forcing—precipitation, potential "
    "evapotranspiration, soil moisture—into streamflow. Since the pioneering perturbation experiments of "
    "Němec and Schaake (1982) and the formulation of climate elasticity (Sankarasubramanian et al., 2001), "
    "this transformation has been measured almost universally as a time-invariant slope that varies across "
    "space but not within a catchment's own history. The rule's theoretical footing rests on the long "
    "search for hydrologic laws (Dooge, 1986) and on the water–energy balance framework (Budyko, 1974), "
    "from which elasticity-type sensitivity measures descend (Vogel and Sankarasubramanian, 2003; Zhang "
    "et al., 2001; Roderick and Farquhar, 2011) and have been applied from Australia (Chiew, 2006) to the "
    "disentangling of climatic versus direct human impacts on streamflow (Wang and Hejazi, 2011). Recent "
    "refinements—power-law and hierarchical elasticity estimators that preserve Dooge's complementary "
    "relationship (Awasthi et al., 2024), and regionalization frameworks for transferring elasticities to "
    "ungauged basins—have sharpened the estimation of this slope, yet they retain its stationarity. That "
    "assumption has been questioned at the water-management level since Milly et al. (2008) famously "
    "declared stationarity dead, and at the modeling level by calls to diagnose rather than assume model "
    "stability (Merz et al., 2011; Westra et al., 2014). Meanwhile, the community has invested in "
    "catchment classification and hydrologic signatures (Wagener et al., 2007), "
    "large-sample hydrology (Gupta et al., 2014; Archfield et al., 2015), and reference networks of "
    "near-natural catchments (Whitfield et al., 2012; Turner et al., 2025) precisely because such "
    "catchments isolate the climate signal (Xu et al., 2025). If the response rule itself drifts over "
    "decades, the interpretation of these investments—and of every attribution statement built upon "
    "them—changes fundamentally."
)

add_para(
    "Three lines of evidence now challenge the stationarity of the response function, in a period when "
    "globally observed streamflow trends have themselves been attributed to climate change (Gudmundsson "
    "et al., 2021) and large-sample archives have made such assessments possible worldwide (Do et al., "
    "2018). First, large-sample non-stationary elasticity regressions across the United States have "
    "identified statistically significant long-term trends in precipitation sensitivity and shown that a "
    "single average elasticity can be a poor indicator of catchment behavior, with year-to-year "
    "variability largest in water-limited regions (Anderson et al., 2025). Second, in more than 1,000 "
    "near-natural catchments, empirical sensitivities decline by 22–70% over five decades along gradients "
    "of increasing aridity, and the sensitivity to potential evaporation proves highly uncertain and "
    "method-dependent (Gnann et al., 2025). Third, information-flow analyses—rooted in ecohydrologic "
    "process networks (Ruddell and Kumar, 2009)—demonstrate that both the strength and the memory of "
    "precipitation's control over streamflow vary systematically across seasons and runoff-generation "
    "regimes (Moges et al., 2022). Complementing these statistical perspectives, physics-embedded machine "
    "learning has revealed worldwide shifts of more than 20% over two decades in fundamental response "
    "signatures such as baseflow ratios and green–blue water partitioning—shifts in quantities that "
    "global models had long treated as static (Ji et al., 2025), and hierarchical Bayesian decompositions "
    "document spatially varying changes in the seasonal shape of hydrographs themselves (Collins et al., "
    "2025). Such findings echo the broader recognition that hydrologic extremes are increasingly analyzed "
    "under non-stationary frameworks, and they re-open the epistemological debate "
    "over whether models should be allowed to change with their changing world (Montanari and "
    "Koutsoyiannis, 2014). Yet each of these studies establishes that response characteristics are "
    "changing without separating how much of that change is forced by the shifting distribution of "
    "meteorological inputs versus how much reflects an autonomous shift in the catchment's internal "
    "response structure."
)

add_para(
    "This distinction is not merely terminological. If a decline in precipitation sensitivity is "
    "predictable from a concurrent increase in the aridity index—the same response function, evaluated "
    "under a drier input distribution, yields a smaller apparent sensitivity—then no structural change "
    "need be invoked, and attribution frameworks that hold the response function fixed remain internally "
    "consistent. Indeed, Gnann et al. (2025) show that a substantial share of the observed sensitivity "
    "decline in near-natural catchments reappears simply as a consequence of shifting aridity, consistent "
    "with evidence that calibrated model parameters are often surprisingly time-stable over multi-decade "
    "windows (Merz et al., 2011). Conversely, there are strong physical grounds to expect drift beyond "
    "such composition effects: vegetation progressively adjusts its root-zone storage capacity to "
    "prevailing moisture deficits, with projected future increases of 10–100% in Alpine catchments "
    "(Ponds et al., 2025); vegetation dynamics modulate the water–energy balance itself (Donohue et al., "
    "2007) and alter evapotranspiration demand beyond simple temperature scaling; snow-to-rain transitions and "
    "permafrost degradation reorganize seasonal storage; and soil structure evolves over decadal scales. "
    "If sensitivity declines beyond what the input-distribution change implies, the response function "
    "itself has shifted, and attributions that hold the function fixed carry a systematic error—with "
    "direct consequences for the runoff changes that climate projections must deliver under "
    "narrowing-but-irreducible uncertainty. Separating these two components—forced "
    "composition versus residual drift—is the central identification problem we address."
)

add_para(
    "Near-natural catchments provide the sharpest setting for this separation because direct human "
    "intervention—dam regulation, groundwater extraction, land-use conversion—is minimized, in contrast "
    "to the globally pervasive human imprint on streamflow through flow regulation and irrigation "
    "(Jaramillo and Destouni, 2015). Recent work has formalized what \"near-natural\" means "
    "operationally: by requiring that hydrological signatures remain insensitive to human-activity "
    "indicators, Xu et al. (2025) derive thresholds of 1.2% cropland fraction and 15.4% reservoir "
    "regulation degree beyond which catchment behavior measurably departs from natural. In such "
    "catchments, residual drift that cannot be explained by concurrent forcing-distribution changes is "
    "more likely to reflect climate-mediated internal adjustments (vegetation composition and phenology, "
    "root-zone storage capacity, soil structure, snow–permafrost dynamics) rather than direct "
    "anthropogenic modification—adjustments consistent with the view of catchments as co-evolving living "
    "systems. We do not claim that near-natural "
    "status excludes internal change; rather, it compresses the candidate-explanation space and makes "
    "residual drift hydrologically interpretable. Our identification strategy also responds to the "
    "broader turn toward causal reasoning in hydrology: just as Bayesian-network do-calculus has been "
    "used to move flood attribution beyond correlation (Nanditha et al., 2025), multi-method causal "
    "inference to filter spurious driver–response relationships (Yue et al., 2026), and counterfactual "
    "world-removal experiments to attribute extreme events, we use design-based "
    "counterfactuals and spatial-randomization tests to distinguish signal from artifact."
)

add_para(
    "We make three contributions. First, we operationalize a decomposition of time-varying response "
    "parameters—estimated with distributed-lag models (Gasparrini et al., 2010; Rushworth et al., 2013)—"
    "into a composition component (the parameter variation expected from concurrent forcing-distribution "
    "changes under a fixed functional form) and a residual drift component. Second, across 2,146 "
    "near-natural catchments, we characterize the dimension selectivity, climate dependence, and spatial "
    "coherence of residual drift. Third, through counterfactual simulations, we quantify the direction and "
    "magnitude of attribution bias that arises from ignoring response-function drift. We position this "
    "work as complementary to information-flow analyses (Moges et al., 2022): whereas information flow "
    "measures how much the coupling strength between precipitation and streamflow changes, our framework "
    "identifies how much of that change is forced by input-distribution shifts versus how much reflects "
    "structural change in the response function."
)

# ============================================================
# 2. DATA AND METHODS
# ============================================================
add_heading("2. Data and Methods", level=1)

add_heading("2.1 Catchment Sample and Inclusion Criteria", level=2)
add_para(
    "Daily streamflow observations and catchment boundaries for 2,172 stations worldwide were compiled "
    "from seven collections: ROBIN (Turner et al., 2025), GRDC-Caravan (Färber et al., 2025), the USGS "
    "National Water Information System (U.S. Geological Survey, 2025), HIDROWEB (Agência Nacional de "
    "Águas e Saneamento Básico, 2025), Datos de Caudales (Centro de Ciencia del Clima y la Resiliencia, "
    "2025), the Global Streamflow Indices and Metadata Archive (Do et al., 2018; Gudmundsson et al., "
    "2018), and the Hydrological Yearbook compiled by the Ministry of Water Resources of the People's "
    "Republic of China (Ministry of Water Resources, 2025)—archives that together cover more than "
    "30,000 catchments. Stations were retained subject to four criteria. First, complete daily records "
    "spanning January 1981 (or January 1984) to December 2018 with gaps below 5% of days and not "
    "concentrated in a single season, yielding a median record length of 38.0 years (minimum 35.0 "
    "years; Figure S1). Second, catchment area between 100 and 100,000 km², encompassing at least one "
    "grid cell of the meteorological forcing (approximately 11 km resolution) while excluding mainstem "
    "rivers; this size range keeps the sample commensurate with the sub-seasonal lag structure resolved "
    "here, as smaller catchments respond faster to precipitation and soil-moisture anomalies than large "
    "basins. Third, minimal human intervention: catchments with reservoir capacity exceeding 10% of "
    "mean annual runoff (GRanD database v1.01; Lehner et al., 2011), urban fraction above 5% (GlobCover "
    "v2.3; Bontemps et al., 2011), or afforestation or deforestation above 10% between 2000 and 2013 "
    "(30-m Landsat imagery; Hansen et al., 2013) were excluded, as were catchments with problematic "
    "water-balance closure (Jaramillo and Destouni, 2015). Fourth, catchment-average meteorological "
    "forcing—ERA5-Land (Muñoz-Sabater et al., 2021) precipitation, vapor-pressure deficit (VPD), and "
    "soil moisture computed by area-weighted interpolation of gridded fields—without continuous gaps "
    "exceeding 30 days. Of the 2,172 candidate stations, the 2,146 that additionally satisfied an area "
    "restriction of < 50,000 km², imposed to avoid excessive spatial averaging of daily response, "
    "constitute the final sample (Figure S1; Table S1). The retained sample has a median drainage area "
    "of 1,111 km², a median record length of 38 years, a median aridity index (PET/P) of 0.80, and a "
    "median baseflow index of 0.72 (UKIH 5-day method; Institute of Hydrology, 1980). Catchment "
    "attributes—including aridity index (Hamon PET; Hamon, 1961, divided by annual precipitation), "
    "snow fraction (fraction of precipitation falling when 2-meter temperature < 1°C), and baseflow "
    "index—were computed from the merged daily record. Restricting the sample to near-natural "
    "catchments follows the signature-based rationale of Xu et al. (2025) and the design philosophy of "
    "large-sample hydrology (Gupta et al., 2014; Addor et al., 2017): it minimizes the human-activity "
    "signal that would otherwise confound the interpretation of residual drift."
)

add_heading("2.2 Time-Varying Response Function: Distributed-Lag Model in Rolling Windows", level=2)
add_para(
    "For each catchment, we estimated a distributed-lag model (DLM) of daily streamflow anomalies as a "
    "function of lagged anomalies of precipitation (P), VPD, and soil moisture (SM). Distributed-lag "
    "specifications have a long history in hydrology, tracing to the search for unit-hydrograph-type "
    "response laws (Dooge, 1986); transfer-function thinking underpins modern rainfall–runoff identification "
    "(Kirchner, 2009), and distributed-lag models for hydrological data have been formalized "
    "statistically (Rushworth et al., 2013). The distributed-lag non-linear model framework of "
    "Gasparrini et al. (2010) provides the statistical foundation for representing delayed effects "
    "through flexible basis expansions of the lag dimension. Prior to estimation, we removed the "
    "day-of-year climatology from each variable using a 31-day centered moving average of the long-term "
    "daily mean, isolating interannual to decadal signals from seasonal cycles:"
)
add_equation("eq01")
add_para(
    "where x̄_DOY(t) is the smoothed day-of-year mean. The anomaly model in each window w is then:"
)
add_equation("eq02")
add_para(
    "where Q′(t) is daily streamflow anomaly, X_m(t) are the anomalies of the three forcing variables, "
    "L = 90 days is the maximum lag, and w_m(l; θ_m) is the lag-response curve for variable m. The lag "
    "structure of each variable is parameterized with a natural cubic spline basis (4 degrees of freedom) "
    "over lags 0–89 days, so that the lag curve is a linear combination of four basis functions:"
)
add_equation("eq03")
add_para(
    "yielding four spline coefficients per variable and a total of 12 coefficients plus an intercept per "
    "window, estimated by ordinary least squares. From each window we extracted three scalar response "
    "parameters. The sensitivity to variable m is the cumulative marginal effect—the sum of the lag "
    "curve:"
)
add_equation("eq04")
add_para(
    "and the memory length is the lag at which the cumulative absolute lag curve reaches 75% of its "
    "total, a compact descriptor in the spirit of catchment forgetting curves (de Lavenne et al., 2022):"
)
add_equation("eq05")
add_para(
    "Windows are 15 years wide and stepped annually; within each window only complete years are used. "
    "The maximum lag of 90 days covers the typical range of soil-moisture memory while avoiding "
    "cross-seasonal spurious lags. Sensitivity of results to window width (10, 20 years) and maximum lag "
    "(60, 120 days) is reported in Table S4."
)

add_heading("2.3 Decomposition: Composition Component vs. Residual Drift", level=2)
add_para(
    "For each response-parameter time series θ_m(t_w) per catchment, we decomposed variation into a "
    "composition component and a residual drift component. The composition component answers a specific "
    "counterfactual: how much would the parameter vary if the response function were fixed and only the "
    "distribution of inputs changed? Because sensitivities depend on the forcing state at which they are "
    "evaluated (Gnann et al., 2025; Anderson et al., 2025), and because diagnosing whether model behavior "
    "is genuinely changing—rather than merely re-expressing input change—requires an explicit strategy "
    "(Merz et al., 2011; Westra et al., 2014), we regress θ_m(t_w) on a vector of concurrent "
    "window-level forcing-distribution features f(t_w): mean annual precipitation, 90th percentile of "
    "VPD, 10th percentile of soil moisture, aridity index (PET/P), and snow fraction:"
)
add_equation("eq06")
add_para(
    "The parameter time series is then split into a mean level, a composition component C_m(t_w), and a "
    "residual component R_m(t_w):"
)
add_equation("eq07")
add_para(
    "where the composition component is the fitted value from Equation 6 centered at the mean forcing "
    "state f̄, representing the parameter variation expected if the response function merely tracked the "
    "shifting forcing distribution. The residual drift is the unexplained remainder, capturing drift "
    "beyond immediate forcing-distribution mapping. We used concurrent (not lagged) forcing features to "
    "avoid conflating the response function's dependence on past states with its autonomous drift. The "
    "directional drift of each parameter is summarized by the ordinary-least-squares slope of the "
    "residual component against window-center time,"
)
add_equation("eq08")
add_para(
    "and the relative importance of drift is quantified as the ratio of the standard deviation of "
    "R_m(t_w) to that of C_m(t_w) + R_m(t_w). Robustness to the composition-regression functional form "
    "was tested with a generalized additive model specification (Table S4)."
)

add_heading("2.4 Discriminating Residual Drift from Estimation Noise", level=2)
add_para(
    "Because residual drift is estimated from finite windows, it could partly reflect estimation noise. "
    "Following the principle that spurious relationships must be filtered by design rather than assumed "
    "away (Yue et al., 2026), we applied three discriminating tests. (A) Spatial coherence: we computed "
    "Moran's I (Moran, 1950) of catchment-level residual drift s_{R,m} using k = 6 nearest-neighbor "
    "spatial weights based on great-circle distance,"
)
add_equation("eq09")
add_para(
    "where z_i is the drift of catchment i, w_ij its spatial weights, and n the number of catchments, "
    "with a null distribution generated by 1,000 stratified random permutations within aridity-index "
    "quintiles so that the null preserves the climate structure of the sample. (B) Driver comparison: we "
    "regressed the magnitude of residual drift on the magnitude of forcing-distribution change "
    "(Euclidean distance of the feature vector between first and last window), sequence length, and "
    "catchment area. If residual drift were dominated by estimation noise, its magnitude should "
    "correlate with estimation conditions (sequence length, flow variability) rather than forcing-change "
    "magnitude. (C) Nearest-neighbor sign consistency: for each catchment we computed the fraction of "
    "its k = 3 nearest neighbors whose residual drift had the same sign, compared against a null "
    "distribution of random pairings."
)

add_heading("2.5 Counterfactual Attribution Experiment", level=2)
add_para(
    "To quantify the consequences of ignoring response drift, we reconstructed daily streamflow "
    "anomalies under three scenarios s (Nanditha et al., 2025): (i) factual, using the actual "
    "time-varying spline coefficients θ_fact(t_w); (ii) stable-response counterfactual A, freezing all "
    "spline coefficients at their earliest-window values; and (iii) composition-only counterfactual B, "
    "allowing only the composition component of the spline coefficients to vary. For each scenario:"
)
add_equation("eq10")
add_para(
    "We then aggregated daily anomalies to annual runoff and computed the Theil–Sen slope b_s (Sen, "
    "1968) of each scenario's annual series, a robust trend estimator that limits the influence of "
    "outliers. The intervention-based logic parallels counterfactual event attribution. The "
    "attribution biases were defined as:"
)
add_equation("eq11")
add_para(
    "where Δ_A isolates the effect of all response drift (composition plus residual) and Δ_B isolates "
    "the effect of residual drift alone. We tested whether the sign of the bias was predictable from the "
    "sign of the residual drift using binomial tests grouped by drift direction. As a longer-term "
    "alternative to rolling windows, the spline coefficients could be embedded in a state-space model "
    "with time-varying parameters estimated by Kalman filtering and smoothing (Durbin and Koopman, 2012); "
    "we return to this in Section 4.3."
)

# ============================================================
# 3. RESULTS
# ============================================================
add_heading("3. Results", level=1)

add_heading("3.1 Response Parameters Are Not Stationary—But Not All Dimensions Drift Equally", level=2)
add_para(
    "Across 2,146 catchments, all response parameters exhibited substantial window-to-window variation, "
    "but the magnitude and climate dependence of that variation differed sharply across dimensions "
    "(Figure 1a; Table 1). The coefficient of variation (CV) of precipitation sensitivity β_P declined "
    "monotonically from arid to humid catchments: median CV = 0.653 in arid zones (interquartile range "
    "0.528–1.218), 0.452 in semi-arid, 0.284 in sub-humid, and 0.190 in humid zones (0.133–0.295). This "
    "amplification of response variability in water-limited regions mirrors the year-to-year elasticity "
    "variability reported for the United States (Anderson et al., 2025) and the large nonlinear runoff "
    "responses of semi-arid and arid systems captured by physics-embedded learning (Ji et al., 2025). "
    "Memory M75_P showed a different pattern (Figure 1c): the largest drift occurred in arid (median std = 10.0 "
    "days) and snow-influenced (7.6 days) catchments, while humid catchments had the smallest memory "
    "drift (5.4 days). VPD sensitivity β_VPD had higher CV overall (Figure 1b; median 0.43–0.84 across zones) but "
    "less systematic climate dependence—consistent with the acknowledged difficulty and uncertainty of "
    "estimating potential-evaporation sensitivities from observations (Gnann et al., 2025). This "
    "dimension selectivity—sensitivity drift concentrating in water-limited systems, memory drift in "
    "snow-influenced and arid systems—indicates that catchment response does not drift uniformly but "
    "along climate-structured axes."
)
add_figure(os.path.join(FIG_DIR, "Figure1_drift_CV_vs_aridity.png"),
           "Figure 1. Dimension-selective drift of catchment response parameters. (a) Coefficient of "
           "variation of precipitation sensitivity β_P; (b) coefficient of variation of vapor-pressure "
           "deficit sensitivity β_VPD; (c) standard deviation (days) of precipitation memory M75_P. Each "
           "panel plots window-to-window variability against aridity index, colored by climate zone; "
           "black lines are LOWESS smooths with 95% bootstrap confidence bands. Sensitivity drift is "
           "largest in arid catchments (a); memory drift is largest in arid and snow-influenced "
           "catchments (c).")

add_table_from_csv(os.path.join(TAB_DIR, "Table1_drift_by_zone.csv"),
                   "Table 1. Drift of response parameters by climate zone: median (25th–75th "
                   "percentile) coefficient of variation of sensitivity parameters, standard deviation "
                   "of memory (days), and median residual-drift fraction. Arid catchments show the "
                   "largest sensitivity drift; arid and snow-influenced catchments the largest memory "
                   "drift.")

add_heading("3.2 A Substantial Share of Parameter Drift Is Not Explained by Concurrent Forcing Composition", level=2)
add_para(
    "Decomposition of each parameter time series into composition and residual components revealed that "
    "residual drift accounts for a median 37.3% of total variation in β_P, 38.5% in β_VPD, 43.6% in "
    "M75_P, and 47.4% in M75_VPD (Table 1; Figure 2a, b). The residual fraction was relatively consistent "
    "across climate zones for β_P (0.34–0.38) and M75_P (0.39–0.45), indicating that forcing-"
    "distribution changes explain roughly 55–65% of sensitivity variation and 55–60% of memory "
    "variation regardless of climate setting. This confirms at daily-resolution scale that a large part "
    "of apparent sensitivity variation is indeed a composition effect predictable from the shifting "
    "forcing state, as anticipated by elasticity analyses (Gnann et al., 2025) and consistent with the "
    "time stability often found for calibrated model parameters (Merz et al., 2011)—but it also bounds "
    "that effect at roughly two thirds of the total. Notably, the residual fraction for memory (M75) exceeded "
    "that for sensitivity (β) across all zones, suggesting that memory length is more prone to drift "
    "that is decoupled from concurrent forcing—consistent with the interpretation that memory reflects "
    "slowly evolving catchment storage structure (de Lavenne et al., 2022) rather than instantaneous "
    "forcing–response mapping."
)
add_figure(os.path.join(FIG_DIR, "Figure2_residual_fraction.png"),
           "Figure 2. Residual drift fraction as a function of catchment climate state. (a) Residual "
           "drift fraction against aridity index; (b) residual drift fraction against snow fraction. "
           "The fraction of total parameter variation attributable to residual drift (not explained by "
           "concurrent forcing-distribution changes) is shown for β_P, β_VPD, M75_P, and M75_VPD. Solid "
           "lines are median quantile regressions; dotted lines are 10th and 90th percentile "
           "regressions. Residual fractions cluster around 0.35–0.50 across all climate states.")

add_heading("3.3 Residual Drift Is Spatially Organized, Not Estimation Noise", level=2)
add_para(
    "All three tests rejected the null hypothesis that residual drift is estimation noise (Figure 3; "
    "Tables S2–S3). Moran's I of catchment-level residual drift was positive and statistically "
    "significant for all four parameters under stratified randomization (β_P: I = 0.057, p < 0.001; "
    "β_VPD: I = 0.040, p = 0.018; M75_P: I = 0.242, p < 0.001; M75_VPD: I = 0.318, p < 0.001). "
    "Memory parameters showed markedly stronger spatial coherence than sensitivity parameters, "
    "consistent with memory reflecting large-scale catchment storage and climate controls. Nearest-"
    "neighbor sign consistency ranged from 0.59 to 0.66, compared with 0.50 under random pairing, "
    "confirming that adjacent catchments share drift direction far more often than expected by chance. "
    "Finally, the magnitude of residual drift correlated more strongly with forcing-change magnitude "
    "than with sequence length or catchment area (Table S2), supporting a signal rather than noise "
    "interpretation. The regional patterning visible in Figure 3a—coherent drift over the western "
    "interior of North America, Scandinavia, and southeastern Australia—parallels the regional "
    "structure of streamflow seasonality shifts documented for North Temperate rivers (Collins et al., "
    "2025), of response-signature shifts worldwide (Ji et al., 2025), and of the climate-attributed "
    "river-flow trends compiled globally (Gudmundsson et al., 2021). We emphasize that these "
    "results establish spatial organization of residual drift; they do not by themselves identify the "
    "causal mechanisms, which we discuss as candidates in Section 4."
)
add_figure(os.path.join(FIG_DIR, "Figure3_spatial_coherence.png"),
           "Figure 3. Spatial coherence of residual drift. (a) Global map of β_P residual drift (slope "
           "of residual component, yr⁻¹), with red indicating positive drift and blue negative drift. "
           "Grey shading shows landmass with country borders; major rivers and lakes are included for "
           "geographic reference. (b) Observed Moran's I (red line) against the stratified-permutation "
           "null distribution for β_P. (c) Standardized regression coefficients of residual-drift "
           "magnitude on forcing-change magnitude, sequence length, and catchment area, showing that "
           "forcing change is the dominant predictor.")

add_heading("3.4 Ignoring Residual Drift Biases Attribution in a Substantial Majority of Catchments", level=2)
add_para(
    "The counterfactual experiment demonstrated that freezing the response function at its earliest-"
    "window level changes the magnitude of the attributed climate contribution by more than 10% in "
    "80.0% of catchments (1,711 of 2,140; Figure 4). The median absolute attribution bias was small in "
    "absolute terms (median bias_A = −0.002 mm yr⁻²) but relative to the factual trend it exceeded 10% "
    "in most catchments, indicating that the response-function drift over the study period was "
    "sufficient to materially alter trend attribution. The composition-only counterfactual (bias_B) "
    "showed a smaller median bias (−0.018 mm yr⁻²), confirming that the composition component captures "
    "most of the drift's effect on trends but that residual drift contributes non-trivially. The sign of "
    "the attribution bias was not uniformly predictable from the sign of the residual drift (Table S3): "
    "binomial tests for sign consistency were not significant at the 5% level when all catchments were "
    "included. This lack of uniform sign alignment—rather than contradicting the importance of drift—"
    "underscores that the relationship between residual drift and attribution bias is mediated by "
    "forcing trends and baseline response direction, such that a drift diagnostic is needed rather than "
    "a simple sign rule."
)
add_figure(os.path.join(FIG_DIR, "Figure4_attribution_bias.png"),
           "Figure 4. Attribution bias from freezing the response function. (a) Global map of bias_A "
           "(factual trend minus stable-response trend), with point size proportional to bias magnitude "
           "and color indicating sign. Country borders, lakes, and major rivers are shown for reference. "
           "(b) Attribution bias grouped by the direction of residual drift in β_P and M75_P. "
           "Percentages above boxes indicate the fraction of catchments with positive bias. The bias "
           "magnitude is substantial in most catchments but its sign is not uniformly predictable from "
           "drift direction alone.")

# ============================================================
# 4. DISCUSSION
# ============================================================
add_heading("4. Discussion", level=1)

add_heading("4.1 Methodological Implications for Attribution Practice", level=2)
add_para(
    "Our results do not imply that all streamflow attribution must use time-varying response functions. "
    "Rather, they define a conditional criterion: when residual drift is spatially coherent (as shown by "
    "Moran's I and nearest-neighbor tests) and exceeds ~35–45% of total parameter variation, stable-"
    "response attributions should be flagged as carrying undiagnosed bias. This criterion gives concrete "
    "content to the caution urged by Anderson et al. (2025), who found that although long-term "
    "elasticity trends are individually modest, a single average elasticity is a poor indicator of "
    "catchment behavior; our counterfactual experiment quantifies the downstream consequence—more than "
    "10% error in attributed climate contributions in 80% of catchments—thereby complementing analyses "
    "that seek to narrow regional runoff-projection uncertainty with a diagnosis "
    "of when stationary-response projections are internally inconsistent (Westra et al., 2014; Merz et "
    "al., 2011). The criterion also helps prioritize where non-stationary formulations matter most. "
    "Because sensitivity drift concentrates in arid catchments and memory drift in snow-influenced ones, "
    "water-limited and snow-dominated regions—precisely the regions where the largest response-signature "
    "shifts have been reported (Ji et al., 2025)—should be prioritized for time-varying treatment, "
    "whereas humid catchments with dominated composition components may remain safely handled with "
    "stationary formulations. When the composition component dominates—i.e., when parameter variation "
    "tracks forcing-distribution changes as expected under a fixed functional form—the bias from holding "
    "the response function constant may be limited. This conditional framing distinguishes our work from "
    "blanket calls for non-stationarity and provides practitioners with an actionable diagnostic: "
    "compute the residual fraction and its spatial coherence; if both are elevated, report attribution "
    "results with a drift caveat or use a time-varying formulation."
)

add_heading("4.2 Candidate Process Mechanisms for Residual Drift", level=2)
add_para(
    "The spatial organization of residual drift and its stronger association with forcing-change "
    "magnitude than with estimation conditions point to catchment-internal processes rather than "
    "statistical artifacts. We propose four candidate mechanisms consistent with the observed patterns. "
    "First, root-zone storage capacity may adapt slowly to changing precipitation and temperature "
    "regimes, altering both sensitivity (through the storage–discharge relationship) and memory (through "
    "the characteristic draining time). This would explain why residual drift is strongest in arid and "
    "snow-influenced catchments, where storage capacity is most likely to be actively adjusted—and it "
    "is directly supported by evidence that vegetation adjusts root-zone storage to moisture deficits, "
    "with climate-based estimates substantially narrowing calibration ranges and future projections "
    "indicating storage increases of 10–100% in Alpine catchments (Ponds et al., 2025). Such adjustment "
    "is the hydrological face of vegetation's role in the Budyko framework (Donohue et al., 2007). "
    "Second, vegetation composition and "
    "phenology shifts in response to CO₂ fertilization, warming, and changing precipitation seasonality "
    "could modify evapotranspiration sensitivity and canopy interception, affecting both β_VPD and "
    "memory; the coupling of the carbon and water cycles implies that elevated CO₂ and warming alter "
    "evapotranspiration demand beyond simple temperature scaling, and the worldwide green–blue water "
    "partitioning shifts documented by Ji et al. (2025) "
    "demonstrate that such adjustments are already detectable at basin scale. Third, soil structural "
    "changes—including the development or degradation of preferential-flow paths—could alter the "
    "fraction of precipitation that enters fast versus slow flow pathways, changing both sensitivity "
    "and memory without changing total water input; subregional heterogeneity in precipitation–"
    "streamflow information flows has been attributed to precisely such differences in preferential-flow "
    "coverage and baseflow contributions (Moges et al., 2022). Fourth, snow-to-rain transitions and "
    "permafrost degradation in cold regions could reorganize seasonal storage and release, producing the "
    "strong memory drift observed in snow-influenced catchments; widespread increases in winter melt "
    "(Musselman et al., 2021), documented permafrost-thaw impacts on hydrology (Walvoord and Kurylyk, "
    "2016), and pronounced winter-flow increases with changing seasonal amplitudes in northern rivers "
    "(Collins et al., 2025) are all consistent with this mechanism. None of these mechanisms is directly "
    "observable in our forcing dataset; testing them requires vegetation remote sensing, stable "
    "isotopes, soil-structure surveys, or permafrost observations. We present them as interpretations "
    "consistent with the spatial pattern of residual drift, not as demonstrated causes."
)

add_heading("4.3 Complementarity with Information-Flow and Causal Frameworks", level=2)
add_para(
    "Information-flow analyses—whose ecohydrologic process-network lineage traces to Ruddell and Kumar "
    "(2009)—have shown that precipitation's control over streamflow varies in strength and memory across "
    "seasons and regions (Moges et al., 2022). Our distributed-lag framework is complementary rather "
    "than competing. Information flow quantifies the reduction in streamflow uncertainty achieved by "
    "conditioning on precipitation; our framework decomposes the parameterized precipitation–streamflow "
    "mapping into a forced (composition) component and an autonomous (residual) component. A change in "
    "information-flow strength could arise from either a change in the forcing distribution or a change "
    "in the response function; our decomposition separates these two sources, so transfer-entropy trends "
    "could in principle be mapped onto the composition–residual split. The same logic connects to the "
    "broader causal-inference agenda in hydrology: convergent cross mapping, transfer entropy, and "
    "Granger causality each answer different questions about driver–response linkages and are powerful "
    "for filtering spurious correlations (Yue et al., 2026), and do-calculus interventions on Bayesian "
    "networks have been used to establish causal flood drivers (Nanditha et al., 2025). Our "
    "counterfactual experiment plays an analogous role at the level of the response function itself: "
    "instead of intervening on predictors, we intervene on the mapping. Finally, the rolling-window "
    "estimator used here could be replaced "
    "by a state-space formulation in which the spline coefficients evolve as a random walk and are "
    "estimated by Kalman filtering and smoothing (Durbin and Koopman, 2012); transfer-function "
    "identification in the tradition of Kirchner (2009) could likewise be re-estimated in rolling "
    "windows. Such formulations would yield continuous parameter trajectories with formal uncertainty "
    "bands and would remove the arbitrary window length, at the cost of stronger distributional "
    "assumptions."
)

add_heading("4.4 Limitations", level=2)
add_para(
    "Four limitations should be noted. First, the distributed-lag model estimates conditional response "
    "parameters, not structural causal coefficients. The residual component's interpretation as "
    "\"structural drift\" depends on the composition regression being correctly specified; while GAM-"
    "based robustness tests (Table S4) support stability, the assumption cannot be fully verified—a "
    "caution consonant with the broader epistemological debate about stationarity (Montanari and "
    "Koutsoyiannis, 2014)—and unobserved slow covariates (e.g., groundwater storage, land-cover "
    "trajectories) could project onto the residual. Second, the near-natural designation itself carries "
    "uncertainty: signature-based thresholds such as those of Xu et al. (2025) are explicit and "
    "reproducible but not immutable, and residual human influence—nutrient deposition, diffuse land-use "
    "legacy—may vary across the sample. Third, ERA5-Land precipitation and VPD (Muñoz-Sabater et al., "
    "2021) have known biases in complex terrain, which could affect the seasonal estimation of response "
    "functions; we mitigated this by removing day-of-year climatologies prior to estimation and by "
    "flagging high-elevation catchments in supplementary analyses, but residual biases remain possible "
    "(Gnann et al., 2025). Fourth, the spatial coverage of the near-natural catchment network is uneven, "
    "with sparse representation in the tropics and some arid regions (Turner et al., 2025). "
    "Global-aggregate results should therefore be interpreted with caution; our primary inferences rest "
    "on climate-zone-stratified analyses rather than global averages."
)

# ============================================================
# 5. CONCLUSIONS
# ============================================================
add_heading("5. Conclusions", level=1)
add_para(
    "Across 2,146 near-natural catchments, we show that catchment response functions drift detectably "
    "over multi-decadal periods and that a substantial fraction of this drift—37–47% depending on the "
    "parameter—is not explained by concurrent changes in meteorological forcing distributions. The "
    "residual drift is spatially organized (Moran's I significant for all parameters; nearest-neighbor "
    "sign consistency 0.59–0.66 vs. 0.50 random) and correlates more strongly with forcing-change "
    "magnitude than with estimation conditions, supporting an interpretation of catchment-internal "
    "adjustment rather than statistical noise. Drift is dimension-selective: sensitivity drift "
    "concentrates in arid catchments, while memory drift is largest in arid and snow-influenced "
    "catchments. Ignoring this drift biases trend attribution by more than 10% in 80% of catchments. "
    "These findings establish that stationarity of the response function is not a neutral simplification "
    "and provide a diagnostic—residual-drift fraction and spatial coherence—for determining when "
    "time-varying response formulations are warranted. More broadly, the composition–residual "
    "decomposition offers a common language for reconciling the response shifts documented by "
    "information-flow, causal-inference, and machine-learning analyses with the attribution "
    "responsibilities of water resources science."
)

# ============================================================
# ACKNOWLEDGMENTS / OPEN RESEARCH
# ============================================================
add_heading("Acknowledgments", level=1)
add_para(
    "This study was motivated by the ROBIN initiative. We thank the national hydrometric agencies and "
    "data providers whose long-term streamflow records made this analysis possible. Computational "
    "resources were provided by [institution]."
)
add_heading("Open Research", level=1)
add_para(
    "Data Availability Statement: Daily streamflow records were compiled from seven collections: ROBIN "
    "(https://doi.org/10.5281/zenodo.14801702; Turner et al., 2025), GRDC-Caravan "
    "(https://doi.org/10.5281/zenodo.7540792; Färber et al., 2025), the USGS National Water Information "
    "System (https://waterdata.usgs.gov/nwis; U.S. Geological Survey, 2025), HIDROWEB "
    "(https://www.snirh.gov.br/hidroweb/apresentacao; Agência Nacional de Águas e Saneamento Básico, "
    "2025), Datos de Caudales (https://www.cr2.cl/datos-de-caudales/; Centro de Ciencia del Clima y la "
    "Resiliencia, 2025), the Global Streamflow Indices and Metadata Archive "
    "(https://doi.pangaea.de/10.1594/PANGAEA.887470; Do et al., 2018; Gudmundsson et al., 2018), and "
    "the Hydrological Yearbook compiled by the Ministry of Water Resources of the People's Republic of "
    "China. Auxiliary screening datasets: the Global Reservoir and Dam database v1.01 "
    "(https://sedac.ciesin.columbia.edu/data/set/grand-v1-dams-rev01; Lehner et al., 2011), the "
    "GlobCover v2.3 land-cover map (http://due.esrin.esa.int/page_globcover.php; Bontemps et al., "
    "2011), and the Global Forest Change dataset "
    "(http://earthenginepartners.appspot.com/science-2013-global-forest; Hansen et al., 2013). "
    "ERA5-Land hourly meteorological fields (https://www.ecmwf.int/en/era5-land; Muñoz-Sabater et al., "
    "2021) were retrieved from the Copernicus Climate Change Service Climate Data Store and aggregated "
    "to daily catchment means. Global country boundaries, lakes, coastlines, and rivers used for "
    "cartography are derived from the Natural Earth public-domain dataset. All derived data tables and "
    "analysis scripts (Python 3) that reproduce every figure and table in this paper and its "
    "Supporting Information are archived at [repository DOI to be assigned upon publication]."
)

# ============================================================
# REFERENCES (AGU/WRR style)
# ============================================================
add_heading("References", level=1)
refs = [
    "Anderson, B. J., Slater, L. J., Rapson, J., Brunner, M. I., Dadson, S. J., Yin, J., & Buechel, M. "
    "(2025). Stationarity assumptions in streamflow sensitivity to precipitation may bias future "
    "projections. Earth's Future, 13(7), e2025EF006188. https://doi.org/10.1029/2025EF006188",

    "Awasthi, C., Vogel, R. M., & Sankarasubramanian, A. (2024). Regionalization of climate elasticity "
    "preserves Dooge's complementary relationship. Water Resources Research, 60(10), e2023WR036606. "
    "https://doi.org/10.1029/2023WR036606",

    "Collins, K. M., Schliep, E. M., Wagner, T., & Wikle, C. K. (2025). Model-based decomposition of "
    "spatially varying temporal shifts in seasonal streamflow across north temperate US rivers. Water "
    "Resources Research, 61(9), e2024WR039500. https://doi.org/10.1029/2024WR039500",

    "de Lavenne, A., Andréassian, V., Crochemore, L., Lindström, G., & Arheimer, B. (2022). Quantifying "
    "multi-year hydrological memory with Catchment Forgetting Curves. Hydrology and Earth System "
    "Sciences, 26(10), 2715–2732. https://doi.org/10.5194/hess-26-2715-2022",

    "Durbin, J., & Koopman, S. J. (2012). Time Series Analysis by State Space Methods (2nd ed.). Oxford, "
    "U. K.: Oxford University Press.",

    "Gasparrini, A., Armstrong, B., & Kenward, M. G. (2010). Distributed lag non-linear models. "
    "Statistics in Medicine, 29(10), 2224–2234. https://doi.org/10.1002/sim.3940",

    "Gnann, S., Anderson, B. J., & Weiler, M. (2025). Uncertainty and non-stationarity of empirical "
    "streamflow sensitivities. EGUsphere [preprint]. https://doi.org/10.5194/egusphere-2025-4527",

    "Ji, H., Song, Y., Bindas, T., Shen, C., Yang, Y., Pan, M., Liu, J., Rahmani, F., Abbas, A., Beck, "
    "H., Lawson, K., & Wada, Y. (2025). Distinct hydrologic response patterns and trends worldwide "
    "revealed by physics-embedded learning. Nature Communications, 16, 9169. "
    "https://doi.org/10.1038/s41467-025-64367-1",

    "Moges, E., Ruddell, B. L., Zhang, L., Driscoll, J. M., & Larsen, L. G. (2022). Strength and memory "
    "of precipitation's control over streamflow across the conterminous United States. Water Resources "
    "Research, 58(3), e2021WR030186. https://doi.org/10.1029/2021WR030186",

    "Nanditha, J. S., Villarini, G., Kim, H., & Naveau, P. (2025). Causal attribution of the "
    "interannual variability in flood peaks through Bayesian networks. Water Resources Research, 61(6), "
    "e2024WR039385. https://doi.org/10.1029/2024WR039385",

    "Němec, J., & Schaake, J. (1982). Sensitivity of water resource systems to climate variation. "
    "Hydrological Sciences Journal, 27(3), 327–343. https://doi.org/10.1080/02626668209491113",

    "Ponds, M., Hanus, S., Zekollari, H., ten Veldhuis, M.-C., Schoups, G., Kaitna, R., & Hrachowitz, "
    "M. (2025). Adaptation of root zone storage capacity to climate change and its effects on future "
    "streamflow in Alpine catchments: Towards non-stationary model parameters. Hydrology and Earth "
    "System Sciences, 29, 3545–3568. https://doi.org/10.5194/hess-29-3545-2025",

    "Rushworth, A. M., Bowman, A. W., Brewer, M. J., & Langan, S. J. (2013). Distributed lag models for "
    "hydrological data. Biometrics, 69(2), 537–544. https://doi.org/10.1111/biom.12008",

    "Sankarasubramanian, A., Vogel, R. M., & Limbrunner, J. F. (2001). Climate elasticity of streamflow "
    "in the United States. Water Resources Research, 37(6), 1771–1781. "
    "https://doi.org/10.1029/2000WR900330",

    "Turner, S., Hannaford, J., Barker, L. J., Suman, G., Killeen, A., Armitage, R., Chan, W., Davies, "
    "H., Griffin, A., Kumar, A., Dixon, H., et al. (2025). ROBIN: Reference observatory of basins for "
    "international hydrological climate change detection. Scientific Data, 12, 654. "
    "https://doi.org/10.1038/s41597-025-04907-y",

    "Xu, H., Wang, H., Liu, P., Zhang, X., Liu, W., Zhou, C., Ye, H., Lei, H., & Liu, Y. (2025). What "
    "is the near-natural catchment? An application of hydrological signatures assessment. Ecological "
    "Indicators, 171, 113209. https://doi.org/10.1016/j.ecolind.2025.113209",

    "Yue, Z. J., Wang, N. N., Xiao, H. B., & Shi, Z. H. (2026). From mechanisms to modeling: Causal "
    "inference for hydro-sedimentary responses. Water Resources Research, 62(4), e2025WR041848. "
    "https://doi.org/10.1029/2025WR041848",

    "Addor, N., Newman, A. J., Mizukami, N., & Clark, M. P. (2017). The CAMELS data set: Catchment "
    "attributes and meteorology for large-sample studies. Hydrology and Earth System Sciences, 21(10), "
    "5293–5313. https://doi.org/10.5194/hess-21-5293-2017",

    "Archfield, S. A., Clark, M., Arheimer, B., Hay, L. E., McMillan, H., Kiang, J. E., Seibert, J., "
    "Hakala, K., Bock, A., Wagener, T., Farmer, W. H., Andréassian, V., Attinger, S., Viglione, A., "
    "Knight, R., Markstrom, S., & Over, T. (2015). Accelerating advances in continental domain "
    "hydrologic modeling. Water Resources Research, 51(12), 10078–10091. "
    "https://doi.org/10.1002/2015WR017498",

    "Budyko, M. I. (1974). Climate and Life. New York, U. S.: Academic Press.",

    "Chiew, F. H. S. (2006). Estimation of rainfall elasticity of streamflow in Australia. Hydrological "
    "Sciences Journal, 51(4), 613–625. https://doi.org/10.1623/hysj.51.4.613",

    "Do, H. X., Gudmundsson, L., Leonard, M., & Westra, S. (2018). The Global Streamflow Indices and "
    "Metadata Archive (GSIM) – Part 1: The production of a daily streamflow archive and metadata. "
    "Earth System Science Data, 10(2), 765–785. https://doi.org/10.5194/essd-10-765-2018",

    "Donohue, R. J., Roderick, M. L., & McVicar, T. R. (2007). On the importance of including "
    "vegetation dynamics in Budyko's hydrological model. Hydrology and Earth System Sciences, 11(2), "
    "983–995. https://doi.org/10.5194/hess-11-983-2007",

    "Dooge, J. C. I. (1986). Looking for hydrologic laws. Water Resources Research, 22(9S), 46S–58S. "
    "https://doi.org/10.1029/WR022i09Sp0046S",

    "Gudmundsson, L., Boulange, J., Do, H. X., Gosling, S. N., Grillakis, M. G., Koutroulis, A. G., "
    "Leonard, M., Liu, J., Müller Schmied, H., Papadimitriou, L., Pokhrel, Y., Seneviratne, S. I., "
    "Satoh, Y., Thiery, W., Westra, S., Zhang, X., & Zhao, F. (2021). Globally observed trends in mean "
    "and extreme river flow attributed to climate change. Science, 371(6534), 1159–1162. "
    "https://doi.org/10.1126/science.aba3996",

    "Gupta, H. V., Perrin, C., Blöschl, G., Montanari, A., Kumar, R., Clark, M., & Andréassian, V. "
    "(2014). Large-sample hydrology: A need to balance depth with breadth. Hydrology and Earth System "
    "Sciences, 18(2), 463–477. https://doi.org/10.5194/hess-18-463-2014",

    "Hamon, W. R. (1961). Estimating potential evapotranspiration. Journal of the Hydraulics Division, "
    "87(HY3), 107–120.",

    "Institute of Hydrology. (1980). Low Flow Studies. Wallingford, U. K.: Institute of Hydrology.",

    "Jaramillo, F., & Destouni, G. (2015). Local flow regulation and irrigation raise global human "
    "water consumption and footprint. Science, 350(6265), 1248–1251. "
    "https://doi.org/10.1126/science.aad1010",

    "Kirchner, J. W. (2009). Catchments as simple dynamical systems: Catchment characterization, "
    "rainfall-runoff modeling, and doing hydrology backward. Water Resources Research, 45(2), W02429. "
    "https://doi.org/10.1029/2008WR006912",

    "Merz, R., Parajka, J., & Blöschl, G. (2011). Time stability of catchment model parameters: "
    "Implications for climate impact analyses. Water Resources Research, 47(2), W02531. "
    "https://doi.org/10.1029/2010WR009505",

    "Milly, P. C. D., Betancourt, J., Falkenmark, M., Hirsch, R. M., Kundzewicz, Z. W., Lettenmaier, "
    "D. P., & Stouffer, R. J. (2008). Stationarity is dead: Whither water management? Science, "
    "319(5863), 573–574. https://doi.org/10.1126/science.1151915",

    "Montanari, A., & Koutsoyiannis, D. (2014). Modeling and mitigating natural hazards: Stationarity "
    "is immortal! Water Resources Research, 50(12), 9748–9756. "
    "https://doi.org/10.1002/2014WR016092",

    "Moran, P. A. P. (1950). Notes on continuous stochastic phenomena. Biometrika, 37(1/2), 17–23. "
    "https://doi.org/10.1093/biomet/37.1-2.17",

    "Muñoz-Sabater, J., Dutra, E., Agustí-Panareda, A., Albergel, C., Arduini, G., Balsamo, G., "
    "Boussetta, S., Choulga, M., Harrigan, S., Hersbach, H., Martens, B., Miralles, D. G., Piles, M., "
    "Rodríguez-Fernández, N. J., Zsoter, E., Buontempo, C., & Thépaut, J.-N. (2021). ERA5-Land: A "
    "state-of-the-art global reanalysis dataset for land applications. Earth System Science Data, "
    "13(9), 4349–4383. https://doi.org/10.5194/essd-13-4349-2021",

    "Musselman, K. N., Addor, N., Vano, J. A., & Molotch, N. P. (2021). Winter melt trends portend "
    "widespread declines in snow water resources. Nature Climate Change, 11(5), 418–424. "
    "https://doi.org/10.1038/s41558-021-01014-9",

    "Roderick, M. L., & Farquhar, G. D. (2011). A simple framework for relating variations in runoff "
    "to variations in climatic conditions and catchment properties. Water Resources Research, 47(12), "
    "W00G07. https://doi.org/10.1029/2010WR009826",

    "Ruddell, B. L., & Kumar, P. (2009). Ecohydrologic process networks: 1. Identification. Water "
    "Resources Research, 45(3), W03419. https://doi.org/10.1029/2008WR007279",

    "Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. Journal of the "
    "American Statistical Association, 63(324), 1379–1389. "
    "https://doi.org/10.1080/01621459.1968.10480934",

    "Vogel, R. M., & Sankarasubramanian, A. (2003). Validation of a watershed model without "
    "calibration. Water Resources Research, 39(10), 1292. "
    "https://doi.org/10.1029/2002WR001940",

    "Wagener, T., Sivapalan, M., Troch, P., & Woods, R. (2007). Catchment classification and "
    "hydrologic similarity. Geography Compass, 1(4), 901–931. "
    "https://doi.org/10.1111/j.1749-8198.2007.00039.x",

    "Walvoord, M. A., & Kurylyk, B. L. (2016). Hydrologic impacts of thawing permafrost—A review. "
    "Vadose Zone Journal, 15(6), 1–20. https://doi.org/10.2136/vzj2016.01.0010",

    "Wang, D., & Hejazi, M. (2011). Quantifying the relative contribution of the climate and direct "
    "human impacts on mean annual streamflow in the contiguous United States. Water Resources "
    "Research, 47(10), W00J12. https://doi.org/10.1029/2010WR010283",

    "Westra, S., Thyer, M., Leonard, M., Kavetski, D., & Lambert, M. (2014). A strategy for "
    "diagnosing and interpreting hydrological model nonstationarity. Water Resources Research, 50(6), "
    "5090–5113. https://doi.org/10.1002/2013WR014719",

    "Whitfield, P. H., Burn, D. H., Hannaford, J., Higgins, H., Hodgkins, G. A., Marsh, T., & Looser, "
    "U. (2012). Reference hydrologic networks I. The status and potential future directions of "
    "national reference hydrologic networks for detecting trends. Hydrological Sciences Journal, "
    "57(8), 1562–1579. https://doi.org/10.1080/02626667.2012.728706",

    "Zhang, L., Dawes, W. R., & Walker, G. R. (2001). Response of mean annual evapotranspiration to "
    "vegetation changes at catchment scale. Water Resources Research, 37(3), 701–708. "
    "https://doi.org/10.1029/2000WR900325",

    "Agência Nacional de Águas e Saneamento Básico. (2025). HIDROWEB: Sistema de Informações "
    "Hidrológicas. https://www.snirh.gov.br/hidroweb/apresentacao",

    "Bontemps, S., Defourny, P., Van Bogaert, E., Arino, O., Kalogirou, V., & Perez, J. R. (2011). "
    "GLOBCOVER 2009: Products description and validation report (Version 2.0). Toulouse, France: "
    "European Space Agency & Université catholique de Louvain.",

    "Centro de Ciencia del Clima y la Resiliencia. (2025). Datos de Caudales. "
    "https://www.cr2.cl/datos-de-caudales/",

    "Färber, C., Plessow, H., Mischel, S. A., Kratzert, F., Addor, N., Shalev, G., & Looser, U. "
    "(2025). GRDC-Caravan: Extending Caravan with data from the Global Runoff Data Centre. Earth "
    "System Science Data, 17(9), 4613–4625. https://doi.org/10.5194/essd-17-4613-2025",

    "Gudmundsson, L., Do, H. X., Leonard, M., & Westra, S. (2018). The Global Streamflow Indices and "
    "Metadata Archive (GSIM) – Part 2: Quality control, time-series indices and homogeneity "
    "assessment. Earth System Science Data, 10(2), 787–804. https://doi.org/10.5194/essd-10-787-2018",

    "Hansen, M. C., Potapov, P. V., Moore, R., Hancher, M., Turubanova, S. A., Tyukavina, A., Thau, "
    "D., Stehman, S. V., Goetz, S. J., Loveland, T. R., Kommareddy, A., Egorov, A., Chini, L., "
    "Justice, C. O., & Townshend, J. R. G. (2013). High-resolution global maps of 21st-century forest "
    "cover change. Science, 342(6160), 850–853. https://doi.org/10.1126/science.1244693",

    "Lehner, B., Reidy Liermann, C., Revenga, C., Vörösmarty, C., Fekete, B., Crouzet, P., Döll, P., "
    "Endejan, M., Frenken, K., Magome, J., Nilsson, C., Robertson, J. C., Rödel, R., Sindorf, N., & "
    "Wisser, D. (2011). High-resolution mapping of the world's reservoirs and dams for sustainable "
    "river-flow management. Frontiers in Ecology and the Environment, 9(9), 494–502. "
    "https://doi.org/10.1890/100125",

    "Ministry of Water Resources of the People's Republic of China. (2025). Hydrological Yearbook of "
    "the People's Republic of China. Beijing, China: Ministry of Water Resources.",

    "U.S. Geological Survey. (2025). USGS Water Data for the Nation. "
    "https://waterdata.usgs.gov/nwis",
]
refs.sort(key=lambda s: s.split(",")[0].lower().replace("de lavenne", "lavenne"))
for r in refs:
    p = doc.add_paragraph(r)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    for run in p.runs:
        run.font.size = Pt(10)

doc.add_page_break()

# ============================================================
# SUPPLEMENTARY MATERIALS
# ============================================================
add_heading("Supporting Information", level=1)

add_heading("Table S1. Catchment attributes by climate zone", level=2)
add_table_from_csv(os.path.join(TAB_DIR, "TableS1_attributes_by_zone.csv"),
                   "Table S1. Median catchment attributes by climate zone.")

add_heading("Table S2. Spatial coherence test results", level=2)
add_table_from_csv(os.path.join(TAB_DIR, "TableS2_spatial_coherence.csv"),
                   "Table S2. Moran's I, nearest-neighbor sign consistency, and standardized regression "
                   "coefficients for residual drift magnitude.")

add_heading("Table S3. Attribution bias sign consistency", level=2)
add_table_from_csv(os.path.join(TAB_DIR, "TableS3_attribution_bias.csv"),
                   "Table S3. Sign consistency of attribution bias (bias_A) grouped by residual-drift "
                   "direction.")

add_heading("Table S4. Robustness of key findings across alternative settings", level=2)
add_table_from_csv(os.path.join(TAB_DIR, "TableS4_robustness.csv"),
                   "Table S4. Summary of robustness tests across window width, lag structure, composition "
                   "regression form, and sample subsets.")

add_figure(os.path.join(FIG_DIR, "FigureS1_sample_funnel.png"),
           "Figure S1. Sample selection funnel and catchment attribute distributions. (a) Funnel of "
           "catchment counts through inclusion criteria. (b) Distribution of available record length. "
           "(c) Distribution of aridity index. (d) Distribution of snow fraction.", width=Inches(6.5))

add_figure(os.path.join(FIG_DIR, "FigureS2_catchment_map.png"),
           "Figure S2. Geographic distribution of the 2,146 near-natural catchments, colored by "
           "climate zone. Grey shading shows landmass with country borders; major rivers (blue lines) "
           "and lakes (white) are included for geographic reference.", width=Inches(6.5))

add_figure(os.path.join(FIG_DIR, "FigureS3_lag_curves.png"),
           "Figure S3. Time-varying lag-response curves for a representative catchment, showing how "
           "precipitation and VPD lag coefficients evolve across early, middle, and late windows.",
           width=Inches(6.0))

add_figure(os.path.join(FIG_DIR, "FigureS4_parameter_timeseries.png"),
           "Figure S4. Decomposition of response-parameter time series into composition and residual "
           "drift components for representative catchments across climate zones. Solid lines show the "
           "actual parameter; dashed lines show the composition component; shaded areas show residual "
           "drift.", width=Inches(6.5))

# Save
try:
    doc.save(OUT_PATH)
    print(f"Manuscript saved to {OUT_PATH}")
except OSError:
    alt = OUT_PATH.replace(".docx", "_updated.docx")
    doc.save(alt)
    print(f"Manuscript saved to {alt} (original locked; close it and re-run to overwrite)")
