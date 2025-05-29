from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
import os
import re
import requests
import random
from urllib.parse import urlparse
from fake_useragent import UserAgent
from PIL import Image
import io
from webdriver_manager.chrome import ChromeDriverManager


# Configuration
# CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver-136"
OUTPUT_FILE_BASE = "yupoo_data"

# Initialiser le générateur d'agent utilisateur
ua = UserAgent()

def get_webp_quality():
    """Demander à l'utilisateur la qualité WebP désirée"""
    print("\n🎨 Configuration de la qualité WebP")
    print("Choisissez la qualité de conversion WebP:")
    print("  100 = Qualité maximale (fichiers plus gros)")
    print("  90  = Très haute qualité (recommandé)")
    print("  80  = Haute qualité (défaut)")
    print("  70  = Bonne qualité")
    print("  60  = Qualité moyenne")
    print("  50  = Qualité basique (fichiers plus petits)")
    print("  30  = Basse qualité")
    
    while True:
        try:
            choice = input("\nEntrez la qualité WebP (30-100): ").strip()
            quality = int(choice)
            
            if 30 <= quality <= 100:
                print(f"✅ Qualité WebP définie à: {quality}")
                if quality >= 90:
                    print("   📈 Très haute qualité - fichiers volumineux")
                elif quality >= 70:
                    print("   📊 Bonne qualité - taille équilibrée")
                else:
                    print("   📉 Qualité réduite - fichiers compacts")
                return quality
            else:
                print("❌ Veuillez entrer un nombre entre 30 et 100")
                
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")

def clean_product_name(name):
    """Nettoyer le nom du produit - MAX 2 MOTS SEULEMENT"""
    if not name or name == "Name not found":
        return "PRODUIT"
    
    try:
        # Supprimer les numéros au début (comme "200")
        name = re.sub(r'^\d+\s*', '', name)
        
        # Supprimer les caractères chinois/japonais/coréens
        name = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+', '', name)
        
        # Supprimer les codes produit (comme HM6803-004, 03YHLS12)
        name = re.sub(r'[A-Z]{2,}\d{4,}-\d{3,}', '', name)
        name = re.sub(r'\d{2,}[A-Z]{2,}\d{2,}', '', name)
        name = re.sub(r'货号[：:][A-Z0-9-]+', '', name)
        
        # Supprimer les tailles (comme 36-45, 36-46, Size 36 46)
        name = re.sub(r'Size\s*\d{2}\s*-?\s*\d{2}', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\d{2}-\d{2}', '', name)
        
        # Supprimer les mots/codes inutiles
        useless_words = ['货号', 'Size', 'Teal', 'Blue', '-', '_']
        for word in useless_words:
            name = re.sub(r'\b' + re.escape(word) + r'\b', '', name, flags=re.IGNORECASE)
        
        # Supprimer les caractères spéciaux et espaces multiples
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        
        # Si le nom est vide après nettoyage, utiliser un nom par défaut
        if not name:
            return "PRODUIT"
        
        # GARDER SEULEMENT LES 2 PREMIERS MOTS SIGNIFICATIFS
        words = [word.upper() for word in name.split() if len(word) > 1]
        
        # Filtrer les mots qui sont juste des numéros ou des codes
        meaningful_words = []
        for word in words:
            # Ignorer les mots qui sont principalement des numéros
            if not re.match(r'^\d+$', word) and not re.match(r'^V?\d+$', word):
                meaningful_words.append(word)
            # Mais garder les versions comme "700V2"
            elif re.match(r'^\d{3}V\d+$', word):
                meaningful_words.append(word)
        
        # Prendre les 2 premiers mots significatifs
        if len(meaningful_words) >= 2:
            result = f"{meaningful_words[0]}_{meaningful_words[1]}"
        elif len(meaningful_words) == 1:
            result = meaningful_words[0]
        else:
            result = "PRODUIT"
        
        # Limiter la longueur totale à 20 caractères
        if len(result) > 20:
            result = result[:20]
        
        return result
        
    except Exception as e:
        print(f"   ⚠️ Erreur lors du nettoyage du nom: {str(e)}")
        return "PRODUIT"

def create_session():
    """Créer une session avec protection anti-bot"""
    session = requests.Session()
    
    # En-têtes améliorés pour contourner la protection anti-bot
    session.headers.update({
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
    })
    
    return session

def is_placeholder_image(response, url):
    """Vérifier si l'image téléchargée est un placeholder"""
    
    # Vérifier la taille du contenu (les images placeholder sont généralement très petites)
    content_length = len(response.content)
    if content_length < 1000:  # Moins de 1KB probablement un placeholder
        print(f"   ⚠️ Image trop petite ({content_length} octets) - probablement un placeholder")
        return True
    
    # Vérifier si redirigé vers des URLs placeholder connues
    placeholder_indicators = [
        'placeholder', 'default', 'error', 'not-found', '404', 
        'forbidden', 'unavailable', 'res/703.gif', 'static/error'
    ]
    
    final_url = response.url.lower()
    for indicator in placeholder_indicators:
        if indicator in final_url:
            print(f"   ⚠️ URL placeholder détectée: {indicator}")
            return True
    
    # Vérifier le type de contenu
    content_type = response.headers.get('Content-Type', '').lower()
    if content_type and not content_type.startswith('image/'):
        print(f"   ⚠️ Type de contenu invalide: {content_type}")
        return True
    
    return False

def convert_to_webp(image_data, quality=80):
    """Convertir les données d'image en format WebP"""
    try:
        print(f"   🔄 Conversion WebP (qualité {quality}): {len(image_data)} octets d'entrée")
        
        # Ouvrir l'image depuis les données binaires
        img = Image.open(io.BytesIO(image_data))
        print(f"   📐 Dimensions originales: {img.size}, Mode: {img.mode}")
        
        # Si l'image a un canal alpha, la convertir en RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            print(f"   🔄 Conversion de {img.mode} vers RGB")
            img = img.convert('RGB')
        
        # Sauvegarder en WebP dans un buffer
        webp_buffer = io.BytesIO()
        img.save(webp_buffer, format='WebP', quality=quality)
        webp_buffer.seek(0)
        
        webp_data = webp_buffer.getvalue()
        print(f"   ✅ Conversion réussie (Q{quality}): {len(webp_data)} octets de sortie")
        
        return webp_data
    except Exception as e:
        print(f"   ❌ ERREUR DE CONVERSION WebP: {str(e)}")
        return None

def download_image(url, output_dir, image_counter, session, folder_name, webp_quality):
    """Télécharger une image avec protection anti-bot et conversion WebP"""
    
    try:
        # Nettoyer et valider l'URL
        url = str(url).strip()
        if not url.startswith(('http://', 'https://')):
            print(f"   ❌ ERREUR: Format d'URL invalide - {url}")
            return False, None, None
        
        # Ajouter un délai aléatoire pour éviter la limitation de débit
        time.sleep(random.uniform(0.5, 2.0))
        
        # Mettre à jour le referrer pour chaque requête
        if 'yupoo.com' in url:
            domain = urlparse(url).netloc
            session.headers.update({'Referer': f'https://{domain}/'})
        
        print(f"   🔄 Téléchargement: {url[:60]}...")
        
        # Première tentative
        response = session.get(url, timeout=30, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"   ❌ ERREUR: Code de statut HTTP {response.status_code}")
            return False, None, None
        
        if is_placeholder_image(response, url):
            print(f"   ❌ ERREUR: Image placeholder détectée")
            return False, None, None
        
        # Convertir en WebP avec la qualité choisie
        print(f"   🔄 Conversion en WebP (qualité {webp_quality})...")
        webp_data = convert_to_webp(response.content, webp_quality)
        
        if webp_data is None:
            print(f"   ❌ ERREUR: Échec de la conversion WebP")
            return False, None, None
        
        # Générer le nom de fichier SIMPLE : img-1.webp, img-2.webp, etc.
        filename = f"img-{image_counter}.webp"
        file_path = os.path.join(output_dir, filename)
        
        # Sauvegarder le fichier WebP
        try:
            with open(file_path, 'wb') as f:
                f.write(webp_data)
            
            # VÉRIFICATION CRITIQUE: S'assurer que le fichier existe réellement
            if not os.path.exists(file_path):
                print(f"   ❌ ERREUR CRITIQUE: Fichier non créé - {file_path}")
                return False, None, None
            
            # Vérifier la taille du fichier sauvegardé
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print(f"   ❌ ERREUR CRITIQUE: Fichier vide - {file_path}")
                os.remove(file_path)  # Supprimer le fichier vide
                return False, None, None
            
            print(f"   ✅ Fichier sauvegardé: {filename} ({file_size} octets, Q{webp_quality})")
            
        except Exception as save_error:
            print(f"   ❌ ERREUR DE SAUVEGARDE: {str(save_error)}")
            return False, None, None
        
        # Générer l'URL du serveur
        server_url = f"http://app.madeinchina-ebook.com/images/{folder_name}/{filename}"
        
        print(f"   ✅ Image téléchargée: {filename}")
        print(f"   🔗 URL serveur: {server_url}")
        return True, filename, server_url
        
    except requests.exceptions.Timeout:
        print(f"   ❌ ERREUR: Timeout lors du téléchargement de {url}")
        return False, None, None
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERREUR: Problème de connexion pour {url}")
        return False, None, None
    except Exception as e:
        print(f"   ❌ ERREUR DE TÉLÉCHARGEMENT pour {url}: {str(e)}")
        return False, None, None

# Setup Chrome options for headless mode
def get_driver():
    options = Options()
    # options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    
    # Activer le mode headless pour que vous puissiez utiliser votre ordinateur normalement
    options.add_argument("--headless")
    
    # Optimisations de performance
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")  # Ne pas charger les images pour un scraping plus rapide
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def detect_pagination(driver, base_url):
    """Détecter si la page a une pagination et retourner le nombre total de pages"""
    print("🔍 Vérification de la pagination...")
    
    try:
        driver.get(base_url)
        time.sleep(3)
        
        # Chercher les éléments de pagination
        pagination_selectors = [
            ".pagination__main",
            ".pagination",
            "[class*='pagination']"
        ]
        
        pagination_found = False
        total_pages = 1
        
        for selector in pagination_selectors:
            try:
                pagination_element = driver.find_element(By.CSS_SELECTOR, selector)
                pagination_found = True
                print("✅ Pagination détectée!")
                
                # Essayer de trouver le nombre total de pages de différentes manières
                page_methods = [
                    # Méthode 1: Chercher le texte "au total X pages"
                    lambda: re.search(r'au total (\d+) pages?', pagination_element.text),
                    # Méthode 2: Chercher le texte "total X pages"
                    lambda: re.search(r'total (\d+) pages?', pagination_element.text.lower()),
                    # Méthode 3: Compter les liens de numéro de page
                    lambda: len(driver.find_elements(By.CSS_SELECTOR, ".pagination__number, .pagination-number, [class*='pagination'] a[href*='page=']")),
                    # Méthode 4: Trouver le numéro de page le plus élevé
                    lambda: max([int(re.search(r'page=(\d+)', link.get_attribute('href')).group(1)) 
                               for link in driver.find_elements(By.CSS_SELECTOR, "a[href*='page=']") 
                               if re.search(r'page=(\d+)', link.get_attribute('href'))], default=1)
                ]
                
                for method in page_methods:
                    try:
                        result = method()
                        if isinstance(result, re.Match):
                            total_pages = int(result.group(1))
                            break
                        elif isinstance(result, int) and result > 0:
                            total_pages = result
                            break
                    except:
                        continue
                
                break
                
            except:
                continue
        
        if not pagination_found:
            print("ℹ️  Aucune pagination trouvée - page unique détectée")
            total_pages = 1
        else:
            print(f"📄 Nombre total de pages détecté: {total_pages}")
        
        return total_pages, pagination_found
        
    except Exception as e:
        print(f"⚠️  Erreur lors de la détection de pagination: {str(e)}")
        return 1, False

def create_output_folder():
    """Créer un dossier personnalisé pour stocker les résultats"""
    print("\n📁 Configuration du dossier")
    print("Choisissez une option:")
    print("1. Entrer un nom de dossier personnalisé")
    print("2. Utiliser un dossier avec horodatage (auto)")
    
    choice = input("Entrez votre choix (1 ou 2): ").strip()
    
    if choice == "1":
        folder_name = input("Entrez le nom du dossier: ").strip()
        if not folder_name:
            folder_name = f"scrape_yupoo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        folder_name = f"scrape_yupoo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Créer le dossier principal
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"✅ Dossier créé: {folder_name}")
        else:
            print(f"📁 Utilisation du dossier existant: {folder_name}")
        
        # Créer le sous-dossier images
        images_dir = os.path.join(folder_name, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            print(f"✅ Dossier images créé: {images_dir}")
        
        return folder_name, images_dir
    except Exception as e:
        print(f"❌ Erreur lors de la création du dossier: {str(e)}")
        print("📁 Utilisation du répertoire actuel à la place")
        images_dir = os.path.join(".", "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        return ".", images_dir

def get_base_url():
    """Obtenir l'URL de base de l'utilisateur"""
    print("\n🌐 Configuration de l'URL")
    print("Entrez l'URL de la catégorie Yupoo à scraper:")
    print("Exemples:")
    print("- https://umkao.x.yupoo.com/categories/511015?isSubCate=true")
    print("- https://umkao.x.yupoo.com/categories/15850?isSubCate=true")
    
    url = input("\nEntrez l'URL: ").strip()
    
    # Nettoyer l'URL - supprimer le paramètre page s'il est présent
    if "page=" in url:
        url = re.sub(r'&page=\d+', '', url)
        url = re.sub(r'\?page=\d+&?', '?', url)
        url = re.sub(r'\?$', '', url)
    
    print(f"✅ URL de base définie: {url}")
    return url

def build_page_url(base_url, page_num, has_pagination):
    """Construire l'URL pour une page spécifique"""
    if not has_pagination or page_num == 1:
        return base_url
    
    # Ajouter le paramètre page
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}page={page_num}"

def scrape_page(driver, base_url, page_num, has_pagination, images_dir, session, folder_name, image_counter, webp_quality):
    """Scraper tous les produits d'une seule page"""
    page_url = build_page_url(base_url, page_num, has_pagination)
    print(f"\n🔍 Scraping de la page {page_num}: {page_url}")
    
    try:
        driver.get(page_url)
        
        # Attendre le chargement des produits
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.album__main")))
        time.sleep(3)
        
        # Obtenir tous les liens produits de cette page
        items = driver.find_elements(By.CSS_SELECTOR, "a.album__main")
        print(f"📦 {len(items)} produits trouvés sur la page {page_num}")
        
        page_data = []
        
        for i, item in enumerate(items, 1):
            try:
                link = item.get_attribute('href')
                print(f"   Traitement de l'article {i}/{len(items)}: {link.split('/')[-1]}")
                
                # Ouvrir la page produit dans un nouvel onglet
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])
                
                # Attendre le chargement de la page
                time.sleep(2)
                
                # Extraire les données du produit avec le compteur d'images et la qualité WebP
                product_data = extract_product_data(driver, link, page_num, images_dir, session, folder_name, image_counter, webp_quality)
                if product_data:
                    page_data.append(product_data)
                    image_counter[0] += 1  # Incrémenter le compteur global
                
                # Fermer l'onglet et retourner à la page principale
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print(f"   ❌ Erreur lors du traitement de l'article {i}: {str(e)}")
                # S'assurer qu'on retourne à la fenêtre principale
                while len(driver.window_handles) > 1:
                    driver.close()
                    if len(driver.window_handles) > 0:
                        driver.switch_to.window(driver.window_handles[0])
                continue
        
        print(f"✅ Page {page_num} terminée: {len(page_data)} articles scrapés")
        return page_data
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping de la page {page_num}: {str(e)}")
        return []

def extract_product_data(driver, link, page_num, images_dir, session, folder_name, image_counter, webp_quality):
    """Extraire les données d'une page produit individuelle"""
    try:
        # Utiliser le bon sélecteur CSS pour le nom du produit
        name = "Nom non trouvé"
        
        # Sélecteur principal - celui que vous avez spécifié
        try:
            element = driver.find_element(By.CSS_SELECTOR, ".showalbumheader__gallerytitle")
            if element.text.strip():
                name = element.text.strip()
        except:
            # Sélecteurs de fallback si le principal échoue
            title_selectors = [
                "span[data-name]",
                ".showalbumheader__title", 
                "h1", "h2"
            ]
            
            for selector in title_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.text.strip():
                        name = element.text.strip()
                        break
                    # Essayer l'attribut data-name si le texte est vide
                    if selector == "span[data-name]":
                        data_name = element.get_attribute('data-name')
                        if data_name:
                            name = data_name
                            break
                except:
                    continue
        
        # Nettoyer le nom du produit (MAX 2 MOTS)
        clean_name = clean_product_name(name)
        
        print(f"   📝 Nom original: {name[:60]}...")
        print(f"   🏷️  Nom nettoyé: {clean_name}")
        print(f"   🖼️  Nom image: img-{image_counter[0]}")
        
        # Extraire l'URL de l'image principale
        image_url = "Image non trouvée"
        image_selectors = [
            ".showalbumheader__gallerycover img",
            ".album-cover img",
            ".gallery img:first-child",
            "img[src*='yupoo.com']"
        ]
        
        for selector in image_selectors:
            try:
                img_element = driver.find_element(By.CSS_SELECTOR, selector)
                src = img_element.get_attribute('src')
                if src and 'yupoo.com' in src:
                    image_url = src
                    print(f"   🖼️  URL image trouvée: {src[:50]}...")
                    break
            except:
                continue
        
        # Télécharger l'image si une URL valide est trouvée
        downloaded_image = None
        server_url = None
        download_status = "❌ ÉCHEC"
        
        if image_url != "Image non trouvée":
            print(f"   🔄 Téléchargement image #{image_counter[0]} (qualité {webp_quality})...")
            success, filename, generated_server_url = download_image(image_url, images_dir, image_counter[0], session, folder_name, webp_quality)
            if success:
                downloaded_image = filename
                server_url = generated_server_url
                download_status = f"✅ RÉUSSI (Q{webp_quality})"
                print(f"   ✅ Image sauvée: {filename}")
            else:
                print(f"   ❌ ÉCHEC du téléchargement")
                download_status = "❌ ÉCHEC - Voir logs détaillés"
        else:
            print(f"   ❌ ERREUR: Aucune URL d'image trouvée")
            download_status = "❌ ÉCHEC - URL introuvable"
        
        # Retourner la structure de données
        return {
            'Nom_Produit': clean_name,
            'Nom_Original': name,
            'Lien_Article': link,
            'URL_Image_Originale': image_url,
            'URL_Image_Serveur': server_url if server_url else "Non disponible",
            'Image_Telecharge': downloaded_image if downloaded_image else "Non téléchargée",
            'Statut_Telechargement': download_status,
            'Qualite_WebP': webp_quality,
            'Numero_Page': page_num,
            'Date_Scraping': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"   ⚠️  Erreur lors de l'extraction des données: {str(e)}")
        return None

def verify_downloaded_files(images_dir):
    """Vérifier les fichiers réellement téléchargés dans le dossier"""
    try:
        if not os.path.exists(images_dir):
            return 0, []
        
        files = os.listdir(images_dir)
        webp_files = [f for f in files if f.endswith('.webp')]
        
        print(f"\n🔍 VÉRIFICATION DU DOSSIER {images_dir}:")
        print(f"   📁 Fichiers WebP trouvés: {len(webp_files)}")
        
        if webp_files:
            print(f"   📋 Liste des fichiers:")
            for i, filename in enumerate(webp_files, 1):
                file_path = os.path.join(images_dir, filename)
                file_size = os.path.getsize(file_path)
                print(f"      {i}. {filename} ({file_size} octets)")
        
        return len(webp_files), webp_files
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification: {str(e)}")
        return 0, []

def save_to_files(all_data, base_filename, output_folder):
    """Sauvegarder les données scrapées dans des fichiers CSV et Excel"""
    if not all_data:
        print("❌ Aucune donnée à sauvegarder!")
        return
    
    df = pd.DataFrame(all_data)
    
    # Chemins des fichiers
    csv_filepath = os.path.join(output_folder, f"{base_filename}.csv")
    excel_filepath = os.path.join(output_folder, f"{base_filename}.xlsx")
    
    # Créer des sauvegardes si les fichiers existent
    for filepath in [csv_filepath, excel_filepath]:
        if os.path.exists(filepath):
            backup_name = f"{filepath.split('.')[0]}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{filepath.split('.')[-1]}"
            os.rename(filepath, backup_name)
            print(f"📋 Fichier existant sauvegardé sous: {backup_name}")
    
    try:
        # Sauvegarder en CSV
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        print(f"📄 CSV sauvegardé dans: {csv_filepath}")
        
        # Sauvegarder en Excel avec formatage
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Produits_Yupoo', index=False)
            
            # Formater le fichier Excel
            workbook = writer.book
            worksheet = writer.sheets['Produits_Yupoo']
            
            # Définir les largeurs de colonnes
            column_widths = {
                'A': 25,  # Nom_Produit
                'B': 60,  # Nom_Original
                'C': 60,  # Lien_Article
                'D': 70,  # URL_Image_Originale
                'E': 70,  # URL_Image_Serveur
                'F': 20,  # Image_Telecharge
                'G': 25,  # Statut_Telechargement
                'H': 15,  # Qualite_WebP
                'I': 12,  # Numero_Page
                'J': 20   # Date_Scraping
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
            
            # Styliser les en-têtes
            from openpyxl.styles import Font, PatternFill, Alignment
            
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
        
        print(f"📊 Excel sauvegardé dans: {excel_filepath}")
        
        print(f"\n🎉 SUCCÈS!")
        print(f"📊 Total d'articles scrapés: {len(all_data)}")
        print(f"📈 Pages scrapées: {df['Numero_Page'].nunique()}")
        
        # Afficher le résumé par page
        page_summary = df.groupby('Numero_Page').size()
        print(f"\n📋 Articles par page:")
        for page, count in page_summary.items():
            print(f"   Page {page}: {count} articles")
        
        # Afficher le résumé par qualité WebP
        if 'Qualite_WebP' in df.columns:
            webp_quality = df['Qualite_WebP'].iloc[0] if len(df) > 0 else "N/A"
            print(f"\n🎨 Qualité WebP utilisée: {webp_quality}")
        
        # Compter les images selon les statuts dans les données
        success_count = len(df[df['Statut_Telechargement'].str.contains('✅', na=False)])
        failed_count = len(df[df['Statut_Telechargement'].str.contains('❌', na=False)])
        
        print(f"\n🖼️  RÉSULTATS DE TÉLÉCHARGEMENT (selon les logs):")
        print(f"   ✅ Images déclarées réussies: {success_count}/{len(all_data)}")
        print(f"   ❌ Images déclarées échouées: {failed_count}/{len(all_data)}")
        print(f"   📊 Taux de réussite déclaré: {(success_count/len(all_data)*100):.1f}%")
        
        # VÉRIFICATION RÉELLE DES FICHIERS
        images_dir = os.path.join(output_folder, "images")
        actual_count, actual_files = verify_downloaded_files(images_dir)
        
        print(f"\n🔍 VÉRIFICATION RÉELLE DES FICHIERS:")
        print(f"   📁 Fichiers réellement présents: {actual_count}/{len(all_data)}")
        print(f"   📊 Taux de réussite RÉEL: {(actual_count/len(all_data)*100):.1f}%")
        
        # Alerte si il y a une différence
        if actual_count != success_count:
            print(f"\n⚠️  ATTENTION: DIFFÉRENCE DÉTECTÉE!")
            print(f"   📊 Déclarés réussis: {success_count}")
            print(f"   📁 Réellement présents: {actual_count}")
            print(f"   🔍 Différence: {success_count - actual_count} fichiers manquants")
            
            if actual_count < success_count:
                print(f"\n🔧 CAUSES POSSIBLES:")
                print(f"   • Erreurs de sauvegarde de fichiers")
                print(f"   • Problèmes de permissions")
                print(f"   • Conversions WebP échouées")
                print(f"   • Fichiers corrompus supprimés")
        
        if failed_count > 0 or actual_count < len(all_data):
            missing_count = len(all_data) - actual_count
            print(f"\n⚠️  ATTENTION: {missing_count} images manquantes!")
            print(f"   Vérifiez la colonne 'Statut_Telechargement' dans le fichier Excel pour plus de détails.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des fichiers: {str(e)}")

def main():
    """Fonction principale de scraping"""
    print("🚀 Scraper Intelligent Yupoo (Images: img-1, img-2... | Noms: MAX 2 MOTS)")
    print("=" * 80)
    
    # Vérifier si Pillow est installé
    try:
        from PIL import Image
    except ImportError:
        print("❌ ERREUR: Pillow n'est pas installé!")
        print("📦 Installez-le avec: pip install Pillow")
        return
    
    # Obtenir l'URL et configurer le dossier
    base_url = get_base_url()
    output_folder, images_dir = create_output_folder()
    
    # NOUVELLE FONCTION: Obtenir la qualité WebP de l'utilisateur
    webp_quality = get_webp_quality()
    
    print(f"\n💾 Dossier de sortie: {output_folder}")
    print(f"🖼️  Dossier des images: {images_dir}")
    print(f"🎨 Qualité WebP: {webp_quality}")
    print("💻 Vous pouvez continuer à utiliser votre ordinateur normalement pendant le scraping!")
    
    start_time = datetime.now()
    all_scraped_data = []
    
    # COMPTEUR GLOBAL POUR LES NOMS D'IMAGES (img-1, img-2, etc.)
    image_counter = [1]  # Utilise une liste pour pouvoir la modifier dans les fonctions
    
    print("\n🔇 Démarrage du navigateur en mode headless...")
    driver = get_driver()
    
    # Créer une session pour le téléchargement d'images
    print("🛡️ Initialisation de la session de téléchargement avec protection anti-bot...")
    session = create_session()
    
    try:
        # Détecter la pagination
        total_pages, has_pagination = detect_pagination(driver, base_url)
        
        if has_pagination:
            print(f"📄 Va scraper {total_pages} pages")
        else:
            print("📄 Va scraper 1 page (pas de pagination)")
        
        print(f"\n🏷️  SYSTÈME DE NOMMAGE:")
        print(f"   📁 Images: img-1.webp, img-2.webp, img-3.webp...")
        print(f"   📝 Produits: MAX 2 mots (ex: YEEZY_700V2)")
        print(f"   🎨 Qualité: {webp_quality}")
        
        # Scraper chaque page
        for page in range(1, total_pages + 1):
            page_data = scrape_page(driver, base_url, page, has_pagination, images_dir, session, os.path.basename(output_folder), image_counter, webp_quality)
            all_scraped_data.extend(page_data)
            
            # Sauvegarder le progrès périodiquement (toutes les 3 pages pour multi-page, ou après page unique)
            if (has_pagination and page % 3 == 0) or (not has_pagination and page == 1):
                temp_csv = os.path.join(output_folder, f"temp_{OUTPUT_FILE_BASE}.csv")
                temp_excel = os.path.join(output_folder, f"temp_{OUTPUT_FILE_BASE}.xlsx")
                
                if all_scraped_data:
                    temp_df = pd.DataFrame(all_scraped_data)
                    temp_df.to_csv(temp_csv, index=False)
                    temp_df.to_excel(temp_excel, index=False)
                    print(f"💾 Progrès sauvegardé (img-{image_counter[0]-1} images traitées, Q{webp_quality})")
            
            # Brève pause entre les pages (seulement s'il y a plus de pages à traiter)
            if page < total_pages:
                time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
    finally:
        driver.quit()
        print("🔇 Navigateur fermé")
    
    # Sauvegarder les résultats finaux
    if all_scraped_data:
        save_to_files(all_scraped_data, OUTPUT_FILE_BASE, output_folder)
        
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n⏱️  Temps total: {duration}")
        print(f"⚡ Temps moyen par article: {duration.total_seconds() / len(all_scraped_data):.2f} secondes")
        print(f"🖼️  Dernier numéro d'image: img-{image_counter[0]-1}")
        print(f"🎨 Qualité WebP utilisée: {webp_quality}")
        
        # Nettoyer les fichiers temporaires
        for temp_file in [f"temp_{OUTPUT_FILE_BASE}.csv", f"temp_{OUTPUT_FILE_BASE}.xlsx"]:
            temp_path = os.path.join(output_folder, temp_file)
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"🗑️  Nettoyé {temp_file}")
        
        print(f"\n📁 Tous les fichiers sauvegardés dans: {output_folder}")
        print(f"🖼️  Images WebP sauvegardées dans: {images_dir}")
        print(f"📋 Format des images: img-1.webp à img-{image_counter[0]-1}.webp (Q{webp_quality})")
    else:
        print("\n❌ Aucune donnée n'a été scrapée!")

if __name__ == "__main__":
    main()