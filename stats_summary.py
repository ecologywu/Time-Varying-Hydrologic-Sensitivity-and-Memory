import pandas as pd, numpy as np

attrs = pd.read_csv(r'C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\catchment_attributes.csv')
dec = pd.read_csv(r'C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\decomposed_params.csv', dtype={'station_id': str})
morans = pd.read_csv(r'C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\morans_I_results.csv', index_col=0)
nn = pd.read_csv(r'C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\nn_consistency_results.csv', index_col=0)
cf = pd.read_csv(r'C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\counterfactual_results.csv', dtype={'station_id': str})

print('=== SAMPLE ===')
print('N catchments:', len(attrs))
print('Area median:', attrs['area_km2'].median(), 'km2')
print('N years median:', attrs['n_years'].median())
print('Aridity median:', round(attrs['aridity_index'].median(), 2))
print('BFI median:', round(attrs['baseflow_index'].median(), 2))

print()
print('=== MORANS I ===')
print(morans[['obs_I','p_value']].to_string())

print()
print('=== NN CONSISTENCY ===')
print(nn[['obs','rand_mean']].to_string())

print()
print('=== ATTRIBUTION BIAS ===')
cf['rel_bias'] = cf['bias_A'] / (np.abs(cf['trend_factual']) + 1e-9)
sig = np.abs(cf['rel_bias']) > 0.1
print('Catchments with |rel bias|>10%:', sig.sum(), '(', round(sig.mean()*100,1), '%)')
print('bias_A median:', round(cf['bias_A'].median(), 4))
print('bias_B median:', round(cf['bias_B'].median(), 4))

print()
print('=== RESIDUAL FRACTION ===')
for p in ['beta_P','beta_VPD','M75_P','M75_VPD']:
    g = dec.groupby('station_id')[[p+'_resid',p+'_comp']].std()
    frac = g[p+'_resid'] / (g[p+'_resid'] + g[p+'_comp'] + 1e-12)
    print(p, ': median resid frac =', round(frac.median(), 3))
