# README.md 

# Transfer Learning for Medical Image Segmentation

## Objective
This project aims to apply transfer learning techniques to a heart-related image dataset, focusing on the segmentation of the left atrium from MRI images. By leveraging pre-trained models and adapting them to this specific task, we aim to reduce training time and enhance model performance, building on prior work from the previous trimester's machine learning pipeline.

## Problem Statement
Heart disease remains a leading cause of mortality globally, necessitating advanced tools for early diagnosis and treatment planning. Accurate segmentation of the left atrium from MRI scans is critical for assessing various heart diseases and planning surgical interventions. This project explores the application of transfer learning to improve the accuracy and efficiency of such segmentation tasks.

## Dataset Description
The dataset consists of MRI images focusing on the left atrium, annotated for segmentation:
- **Source**: King’s College London
- **Modality**: MRI
- **Labels**: Background, Left Atrium
- **Training Images**: 20
- **Test Images**: 10
- **Format**: `.nii.gz`
- **License**: CC-BY-SA 4.0

## Models Selected for Transfer Learning
1. **U-Net**: Chosen for its effectiveness in medical image segmentation due to its symmetric expanding path that helps in precise localization.
2. **VGG19
