# Blur Detection Challenge Set — Ground Truth Manifest

10 synthetic documents (5 sharp, 5 blurry) located in `sample_images/`, each engineered to target a specific
failure mode identified during pipeline design. Use these to sanity-check your
blur-detection stages before calibrating on real data.

| File | Ground Truth | What it tests |
|---|---|---|
| sharp_01_blank_margins.png | SHARP | Large blank margins / sparse content — tests blank-tile-trap false reject |
| sharp_02_glare_but_infocus.png | SHARP | In-focus text with a specular glare spot — tests glare-inflated-variance false PASS on the wrong signal / should be flagged by glare stage, not sharpness |
| sharp_03_high_resolution.png | SHARP | 3200x4000 in-focus scan — tests resolution-dependent Laplacian bias (must be canonically resized before scoring) |
| sharp_04_dense_text_anisotropic.png | SHARP | Dense horizontal text lines, naturally anisotropic gradients — tests false motion-blur flag on clean text |
| sharp_05_near_min_resolution.png | SHARP | Small but crisp scan near typical minimum-resolution threshold — tests resolution floor edge case |
| blur_01_horizontal_motion.png | BLURRY | Pure horizontal motion blur — tests directional-blur blindness of isotropic Laplacian |
| blur_02_noise_masked.png | BLURRY | Genuinely blurred + high sensor noise — noise inflates raw Laplacian variance, masking the real blur |
| blur_03_regional_partial.png | BLURRY | Sharp top, blurry bottom third — tests whether global/mean scoring misses regional blur (needs tiled scoring) |
| blur_04_lowres_plus_blur.png | BLURRY | Heavy downscale/upscale artifacts + mild blur — genuinely unreadable, tests resolution+sharpness combined failure |
| blur_05_glare_plus_blur.png | BLURRY | Real blur combined with a glare spot — the single hardest case: glare's sharp edge can offset the low text-region variance |
