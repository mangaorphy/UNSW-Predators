# UNSW Predators - Camera Trap Image Classification

This project implements and compares classical machine learning and deep learning approaches for classifying wildlife camera trap images from the UNSW Predators dataset.

## Dataset Overview

The **UNSW Predators** dataset contains 131,802 images from 82 camera locations in Myall Lakes National Park, New South Wales, Australia. The dataset includes five wildlife categories:

| Category | Number of Images |
|----------|-----------------|
| Goanna   | 84,361          |
| Dingo    | 24,540          |
| Quoll    | 16,406          |
| Fox      | 4,421           |
| Possum   | 2,074           |

### Data Collection

Images were collected by Brendan Alting through the **Myall Lakes Dingo/Dapin Project** using Browning Strike Force HD Pro cameras deployed from December 2022 to March 2023.

**Funding & Ethics:**
- Funded by: Oatley Flora and Fauna Society, Australian Wildlife Society, Taronga Conservation Society Australia, and UNSW Research Technology Services AWS cloud grant
- Conducted under approval 22/102A from UNSW Animal Ethics Committee

**Dataset Source:** [LILA BC - UNSW Predators](https://lila.science/datasets/unsw-predators/)

## Project Structure

```
UNSW-Predators/
├── download_unsw.py                      # Script to download 50% sample from Google Cloud
├── organize_unsw.py                       # Script to organize images into class folders
├── UNSW_Predators_Classical_models.ipynb  # Classical ML models (Logistic Regression, SVC)
├── UNSW_Predators_CNNDEEP.ipynb          # Deep learning models (CNN, ResNet50, EfficientNetB0)
└── README.md
```

## 🚀 Data Preparation

### 1. Downloading the Dataset

The `download_unsw.py` script downloads a 50% sample of images from each class using Google Cloud Storage:

```bash
python download_unsw.py
```

**Features:**
- Downloads 50% sample per class (reproducible with seed=42)
- Live progress monitoring during download
- Resumable downloads (skip already downloaded files)
- Uses `gsutil` for fast parallel downloads from Google Cloud

**Prerequisites:** Install Google Cloud SDK ([instructions](https://cloud.google.com/sdk/docs/install))

### 2. Organizing Images

The `organize_unsw.py` script organizes downloaded images into class-specific folders:

```bash
python organize_unsw.py
```

This creates the following structure:
```
unsw_images_organized/
├── dingo/
├── fox/
├── goanna/
├── possum/
└── quoll/
```

### 3. Image Preprocessing

All images were resized to **224×224 pixels** to enable faster training while maintaining aspect ratio characteristics for feature extraction and model training.

## Models Implemented

### Classical Machine Learning Models

Implemented in `UNSW_Predators_Classical_models.ipynb`

#### Feature Extraction Approaches:
1. **Raw Pixel Features** - Flattened pixel values as input
2. **Histogram of Oriented Gradients (HOG)** - Edge and gradient features
3. **Color Histograms** - RGB/HSV color distribution features
4. **Combined Features** - HOG + Color histograms

#### Classifiers:
1. **Logistic Regression** - Multi-class classification with regularization
2. **Support Vector Classifier (SVC)** - With RBF kernel for non-linear decision boundaries

### Deep Learning Models

Implemented in `UNSW_Predators_CNNDEEP.ipynb`

#### 1. Custom CNN Architecture
- Built from scratch with convolutional, pooling, and dense layers
- Optimized for the specific characteristics of camera trap images

#### 2. Transfer Learning Models
- **ResNet50** - 50-layer residual network pre-trained on ImageNet
- **EfficientNetB0** - Compound scaled architecture balancing depth, width, and resolution

**Approach:** Fine-tuning pre-trained models on the UNSW Predators dataset to leverage learned features from large-scale image datasets.

## Methodology

### Classical ML Pipeline:
1. Load and preprocess images (resize to 224×224)
2. Extract features using various techniques
3. Normalize/standardize features
4. Train classifiers with cross-validation
5. Evaluate performance on test set

### Deep Learning Pipeline:
1. Load and preprocess images
2. Data augmentation (rotation, flip, zoom.)
3. Train models with:
   - Early stopping
   - Learning rate scheduling
   - Regularization (dropout, batch normalization)
4. Evaluate and compare architectures

## Objectives

- Compare classical ML vs. deep learning performance on camera trap images
- Evaluate different feature extraction techniques for classical ML
- Assess transfer learning effectiveness for wildlife classification
- Handle class imbalance in real-world ecological datasets
- Optimize for computational efficiency with image resizing

## References

- Alting, B., et al. (2023). UNSW Predators Dataset. LILA BC.
- Dataset available at: https://lila.science/datasets/unsw-predators/

## License

This project uses the UNSW Predators dataset. Please refer to the original dataset documentation for licensing information.

## Acknowledgments

- **Brendan Alting** for dataset collection
- **Myall Lakes Dingo/Dapin Project**
- Funding organizations: Oatley Flora and Fauna Society, Australian Wildlife Society, Taronga Conservation Society Australia, UNSW ResTech
- **LILA BC** for hosting the dataset

---

*Project created for wildlife classification research using classical machine learning and deep learning approaches.*
