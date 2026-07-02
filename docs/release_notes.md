# Release notes
16/11/20222: beta upload to Flywheel instance 
    - Niall Bourke & Pablo Velasco
    - Non-functioning skeleton of gear for debugging

13/01/2026: v 0.1.10
    - Resampling relies on voxels dimensions of the image (instead of the default 1.5)

1/4/2026: v 0.1.11
    - Reverting resampling to use 1mm default, due to Hyperfine upsampling change.

3/6/2026: v 0.1.12
    - Added metadata to output file (MR and modality)

3/6/2026: v 0.1.13
    - Added INTENT : Structural to metadata to output file

2/7/2026: v 0.1.14
    - read-write permission activated to allow session note + info recording from patient_comments dcm header