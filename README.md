# Yupoo Scraper - Guide Complet d'Installation & Utilisation

**Scraper intelligent de produits Yupoo avec téléchargement d'images, conversion WebP et export Excel**

## 📋 Table des Matières
- [Fonctionnalités](#-fonctionnalités)
- [Prérequis](#-prérequis)
- [Installation Windows](#-installation-windows)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure de Sortie](#-structure-de-sortie)
- [Dépannage](#-dépannage)
- [Exemples](#-exemples)

---

## ✨ Fonctionnalités

- 🖼️ **Nommage Intelligent des Images**: Télécharge les images sous `img-1.webp`, `img-2.webp`, `img-3.webp`
- 📝 **Noms de Produits Propres**: Nettoie automatiquement et limite les noms de produits à maximum 2 mots
- 🔄 **Conversion WebP**: Convertit toutes les images en format WebP pour des fichiers plus petits
- 📊 **Formats d'Export Multiples**: Sauvegarde les données en CSV et Excel
- 🛡️ **Protection Anti-Bot**: Délais et en-têtes intégrés pour éviter la détection
- 📄 **Support de Pagination**: Détecte et scrape automatiquement plusieurs pages
- 🌐 **URLs Serveur**: Génère des URLs serveur prêtes à utiliser pour les images
- 💾 **Sauvegarde de Progrès**: Sauvegarde le progrès périodiquement pour éviter la perte de données

---

## 🛠️ Prérequis

### Configuration Système
- **Windows 10/11**
- **Python 3.8+**
- **Google Chrome** ou **Microsoft Edge**
- **Connexion Internet Stable**

### Packages Python
Tous les packages requis seront installés automatiquement (voir étapes d'installation ci-dessous)

---

## 💻 Installation Windows

### Étape 1: Installer Python
1. Téléchargez Python depuis [python.org](https://www.python.org/downloads/windows/)
2. **IMPORTANT**: Cochez "Add Python to PATH" durant l'installation
3. Vérifiez l'installation en ouvrant l'Invite de Commandes et tapez:
   ```cmd
   python --version
   ```

### Étape 2: Télécharger ChromeDriver
1. Vérifiez votre version de Chrome: Chrome → Aide → À propos de Google Chrome
2. Téléchargez le ChromeDriver correspondant depuis [chromedriver.chromium.org](https://chromedriver.chromium.org/)
3. Extrayez `chromedriver.exe` vers `C:\chromedriver\chromedriver.exe`

### Étape 3: Créer le Répertoire du Projet
```cmd
mkdir C:\yupoo_scraper
cd C:\yupoo_scraper
```

### Étape 4: Créer l'Environnement Virtuel
```cmd
python -m venv venv
venv\Scripts\activate
```

### Étape 5: Créer le Fichier requirements.txt
Créez un fichier `requirements.txt` avec le contenu suivant:
```txt
pandas>=2.0.0
openpyxl>=3.1.0
selenium>=4.15.0
requests>=2.31.0
fake-useragent>=1.4.0
Pillow>=10.0.0
```

### Étape 6: Installer les Packages Requis
```cmd
pip install -r requirements.txt
```

### Étape 7: Sauvegarder le Script
1. Créez un fichier appelé `scraper.py` dans `C:\yupoo_scraper\`
2. Copiez et collez le code Python fourni
3. **IMPORTANT**: Modifiez ces lignes dans le script pour Windows:

```python
# Changez cette ligne (autour de la ligne 18):
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver-136"
# VERS:
CHROMEDRIVER_PATH = "C:\\chromedriver\\chromedriver.exe"

# Changez cette ligne (autour de la ligne 211):
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
# VERS (pour Chrome):
# options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# OU (pour Edge):
# options.binary_location = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
# OU commentez cette ligne pour utiliser Chrome par défaut
```

---

## ⚙️ Configuration

### Option 1: Utiliser Chrome par Défaut (Recommandé)
1. Assurez-vous que Chrome est installé normalement
2. Commentez ou supprimez la ligne `binary_location`:
```python
# options.binary_location = "..."  # Commentez cette ligne
```

### Option 2: Utiliser un Chemin Browser Personnalisé
Trouvez l'exécutable de votre navigateur et mettez à jour le chemin:

**Pour Chrome:**
```python
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
```

**Pour Edge:**
```python
options.binary_location = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
```

### Configuration du Chemin ChromeDriver
Mettez à jour le chemin ChromeDriver dans le script:
```python
CHROMEDRIVER_PATH = "C:\\chromedriver\\chromedriver.exe"
```

---

## 🚀 Utilisation

### Étape 1: Activer l'Environnement Virtuel
```cmd
cd C:\yupoo_scraper
venv\Scripts\activate
```

### Étape 2: Lancer le Script
```cmd
python scraper.py
```

### Étape 3: Suivre les Invites Interactives

#### 🌐 Configuration de l'URL
Le script demandera l'URL de la catégorie Yupoo:
```
🌐 Configuration de l'URL
Entrez l'URL de la catégorie Yupoo à scraper:
Exemples:
- https://umkao.x.yupoo.com/categories/511015?isSubCate=true
- https://umkao.x.yupoo.com/categories/15850?isSubCate=true

Entrez l'URL: 
```

**Exemples d'URLs:**
- `https://umkao.x.yupoo.com/categories/511015?isSubCate=true`
- `https://vendeur.x.yupoo.com/categories/12345?isSubCate=true`

#### 📁 Configuration du Dossier
Choisissez l'option de dossier de sortie:
```
📁 Configuration du dossier
Choisissez une option:
1. Entrer un nom de dossier personnalisé
2. Utiliser un dossier avec horodatage (auto)

Entrez votre choix (1 ou 2): 
```

**Recommandations:**
- Choisissez **1** pour un nom de dossier personnalisé (ex: "chaussures_nike", "collection_yeezy")
- Choisissez **2** pour un dossier avec horodatage automatique

### Étape 4: Surveiller le Progrès
Le script affichera le progrès en temps réel:
```
🏷️  SYSTÈME DE NOMMAGE:
   📁 Images: img-1.webp, img-2.webp, img-3.webp...
   📝 Produits: MAX 2 mots (ex: YEEZY_700V2)

🔍 Scraping de la page 1: https://umkao.x.yupoo.com/categories/511015?isSubCate=true
📦 15 produits trouvés sur la page 1

   📝 Nom original: 200 YEEZY 700V2 Teal Blue 700V2 03YHLS12 Size 36-46...
   🏷️  Nom nettoyé: YEEZY_700V2
   🖼️  Nom image: img-1
   ✅ Image sauvée: img-1.webp
```

---

## 📁 Structure de Sortie

Après un scraping réussi, vous obtiendrez:

```
nom_de_votre_dossier/
├── yupoo_data.csv           ← Données brutes en format CSV
├── yupoo_data.xlsx          ← Fichier Excel formaté avec style
└── images/                  ← Dossier des images téléchargées
    ├── img-1.webp          ← Image du premier produit
    ├── img-2.webp          ← Image du deuxième produit
    ├── img-3.webp          ← Image du troisième produit
    └── ...                 ← Plus d'images
```

### 📊 Colonnes du Fichier Excel
| Colonne | Description | Exemple |
|---------|-------------|---------|
| `Nom_Produit` | Nom de produit nettoyé (max 2 mots) | `YEEZY_700V2` |
| `Nom_Original` | Nom de produit original du site web | `200 YEEZY 700V2 Teal Blue...` |
| `Lien_Article` | Lien direct vers la page produit | `https://umkao.x.yupoo.com/...` |
| `URL_Image_Originale` | URL d'image originale de Yupoo | `https://photo.yupoo.com/...` |
| `URL_Image_Serveur` | URL serveur générée | `http://app.madeinchina-ebook.com/images/dossier/img-1.webp` |
| `Image_Telecharge` | Nom de fichier image téléchargée | `img-1.webp` |
| `Statut_Telechargement` | Statut de téléchargement | `✅ RÉUSSI` ou `❌ ÉCHEC` |
| `Numero_Page` | Numéro de page | `1`, `2`, `3`... |
| `Date_Scraping` | Horodatage du scraping | `2025-05-28 14:30:45` |

### 🌐 URLs Serveur
Les URLs générées suivent ce format:
```
http://app.madeinchina-ebook.com/images/{nom_dossier}/{nom_image}
```

**Exemples:**
- `http://app.madeinchina-ebook.com/images/chaussures_nike/img-1.webp`
- `http://app.madeinchina-ebook.com/images/chaussures_nike/img-2.webp`

---

## 🛠️ Dépannage

### Problèmes Courants & Solutions

#### ❌ Problèmes ChromeDriver
**Erreur:** `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solutions:**
1. **Vérifiez le chemin ChromeDriver:**
   ```python
   CHROMEDRIVER_PATH = "C:\\chromedriver\\chromedriver.exe"
   ```
2. **Vérifiez que le fichier existe:**
   ```cmd
   dir "C:\chromedriver\chromedriver.exe"
   ```
3. **Téléchargez la version correcte** correspondant à votre version de Chrome

#### ❌ Problèmes de Chemin Browser
**Erreur:** `selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary`

**Solutions:**
1. **Utilisez Chrome par défaut** (commentez binary_location):
   ```python
   # options.binary_location = "..."  # Commentez cette ligne
   ```
2. **Trouvez le chemin Chrome correct:**
   ```cmd
   dir "C:\Program Files\Google\Chrome\Application\chrome.exe"
   dir "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
   ```

#### ❌ Erreurs d'Import
**Erreur:** `ModuleNotFoundError: No module named 'selenium'`

**Solution:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

#### ❌ Erreurs de Permission
**Erreur:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**
1. **Exécuter en tant qu'Administrateur:** Clic droit sur Invite de Commandes → "Exécuter en tant qu'administrateur"
2. **Changer le dossier de sortie** vers vos Documents ou Bureau
3. **Vérifier les paramètres antivirus** (peut bloquer la création de fichiers)

#### ❌ Problèmes Réseau/Téléchargement
**Erreur:** Timeouts de connexion ou échecs de téléchargement

**Solutions:**
1. **Vérifiez la connexion internet**
2. **Essayez différentes URLs Yupoo**
3. **Redémarrez le script** (le progrès est sauvegardé automatiquement)
4. **Vérifiez les paramètres du pare-feu**

#### ❌ Problèmes de Conversion d'Images
**Erreur:** `PIL.UnidentifiedImageError: cannot identify image file`

**Solutions:**
1. **Installer/réinstaller Pillow:**
   ```cmd
   pip uninstall pillow
   pip install pillow>=10.0.0
   ```
2. **Vérifiez les URLs d'images** dans le fichier Excel
3. **Certaines images peuvent être corrompues** sur le site web source

#### ❌ Problèmes de Version Python
**Erreur:** `SyntaxError` ou problèmes de compatibilité

**Solutions:**
1. **Vérifiez la version Python:**
   ```cmd
   python --version
   ```
2. **Assurez-vous d'avoir Python 3.8+**
3. **Mettez à jour Python** si nécessaire

---

## 📝 Exemples

### Exemple 1: Catégorie Nike
```
URL: https://vendeur.x.yupoo.com/categories/12345?isSubCate=true
Dossier: collection_nike
Résultat: 25 produits scrapés, 23 images téléchargées avec succès
```

### Exemple 2: Catégorie Yeezy
```
URL: https://umkao.x.yupoo.com/categories/511015?isSubCate=true
Dossier: yeezy_2024
Résultat: 18 produits scrapés, 18 images téléchargées avec succès
```

### Exemples de Nettoyage de Noms de Produits
| Nom Original | Nom Nettoyé |
|--------------|-------------|
| `200 YEEZY 700V2 Teal Blue 700V2 03YHLS12 Size 36-46` | `YEEZY_700V2` |
| `NIKE AIR MAX 90 White Black Size 40-45 货号:HM6803` | `NIKE_AIRMAX` |
| `Jordan 1 High OG Chicago Red White Black` | `JORDAN_HIGH` |
| `300 Air Force 1 Low Triple White 36-45` | `AIR_FORCE` |
| `Adidas Ultra Boost 22 Core Black Size 39-46` | `ADIDAS_ULTRA` |

---

## ⚡ Conseils de Performance

1. **Internet Stable**: Assurez-vous d'avoir une connexion stable pour de meilleurs résultats
2. **Fermer les Autres Programmes**: Pour de meilleures performances durant le scraping
3. **Surveiller le Progrès**: Vérifiez la sortie console pour détecter les problèmes
4. **Sauvegarder les Données**: Les fichiers Excel et CSV sont automatiquement sauvegardés
5. **Capacité de Reprise**: Redémarrez le script si interrompu (le progrès est sauvegardé)

---

## 📦 Structure des Fichiers du Projet

```
C:\yupoo_scraper\
├── venv\                    ← Environnement virtuel Python
├── requirements.txt         ← Liste des packages requis
├── scraper.py              ← Script principal
├── README.md               ← Ce guide
└── resultats\              ← Dossiers de sortie (créés automatiquement)
    ├── collection_nike\
    ├── yeezy_2024\
    └── ...
```

---

## 🔄 Mises à Jour et Maintenance

### Pour Mettre à Jour les Packages:
```cmd
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Pour Vérifier les Versions:
```cmd
pip list
```

### Pour Nettoyer l'Environnement:
```cmd
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🆘 Support

Si vous rencontrez des problèmes:

1. **Consultez ce README** pour les solutions communes
2. **Vérifiez tous les chemins** dans le script sont corrects pour Windows
3. **Assurez-vous que toutes les dépendances** sont installées
4. **Vérifiez la connexion internet** et l'accessibilité du site Yupoo
5. **Essayez différentes URLs Yupoo** si une ne fonctionne pas

### Vérifications Rapides:
```cmd
# Vérifier Python
python --version

# Vérifier les packages
pip list

# Vérifier ChromeDriver
dir "C:\chromedriver\chromedriver.exe"

# Vérifier Chrome
dir "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

---

## 📄 Licence

Ce script est destiné à un usage éducatif et personnel uniquement. Veuillez respecter les conditions d'utilisation de Yupoo et utiliser de manière responsable.

---

**Bon Scraping! 🎉**