"""
Epic Games Free Games Scraper - AWS Lambda Function
Versão Production-Ready com API GraphQL Oficial

Configuração Lambda Recomendada:
- Runtime: Python 3.12
- Memória: 128 MB
- Timeout: 10 segundos
- Nenhuma Layer necessária (usa apenas stdlib)

Custo Estimado: FREE TIER permanente
- ~1 segundo por execução
- Sem dependências externas
- 128MB suficiente

Autor: Jonathas Rocha
Data: 2025-11-17
"""

import json
import urllib.request
import urllib.error
import gzip
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da AWS Lambda Function

    Args:
        event: Evento Lambda (não utilizado nesta versão)
        context: Contexto Lambda com informações de runtime

    Returns:
        Dict com statusCode, headers e body (JSON)

    Exemplo de Resposta Sucesso:
        {
            "statusCode": 200,
            "headers": {...},
            "body": "{\"scraped_at\": \"2025-11-17T...\", \"total_games\": 2, ...}"
        }

    Exemplo de Resposta Erro:
        {
            "statusCode": 500,
            "headers": {...},
            "body": "{\"error\": \"Mensagem de erro\", \"details\": \"...\"}"
        }
    """
    logger.info("🚀 Iniciando Epic Games Free Scraper")
    logger.info(f"Request ID: {getattr(context, 'aws_request_id', 'local') if context else 'local'}")
    logger.info(f"HTTP Method: {event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')}")

    # Handle CORS preflight
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }

    try:
        games = get_free_games_api()
        
        response_body = {
            'scraped_at': datetime.now().isoformat(),
            'total_games': len(games),
            'games': games,
            'source': 'Epic Games Store API',
            'locale': 'pt-BR'
        }
        
        logger.info(f"✅ Scraping concluído: {len(games)} jogos encontrados")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'max-age=3600'  # Cache de 1 hora
            },
            'body': json.dumps(response_body, ensure_ascii=False, indent=2)
        }
        
    except urllib.error.HTTPError as e:
        logger.error(f"❌ HTTP Error: {e.code} - {e.reason}")
        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Erro ao acessar API da Epic Games',
                'details': f'HTTP {e.code}: {e.reason}',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except urllib.error.URLError as e:
        logger.error(f"❌ URL Error: {e.reason}")
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Erro de conexão com Epic Games',
                'details': str(e.reason),
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON Decode Error: {e}")
        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Erro ao processar resposta da API',
                'details': f'JSON inválido na linha {e.lineno}',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {type(e).__name__}: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Erro interno do servidor',
                'details': str(e),
                'type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            })
        }


def get_free_games_api() -> List[Dict[str, Any]]:
    """
    Busca jogos gratuitos usando a API GraphQL oficial da Epic Games
    
    Returns:
        Lista de dicionários com informações dos jogos gratuitos
        
    Raises:
        urllib.error.HTTPError: Se a API retornar erro HTTP
        urllib.error.URLError: Se houver erro de conexão
        json.JSONDecodeError: Se a resposta não for JSON válido
        
    Estrutura do Retorno:
        [
            {
                'title': str,
                'description': str,
                'url': str,
                'slug': str,
                'original_price': str,
                'discount_price': str,
                'publisher': str,
                'developer': str,
                'thumbnail': str (opcional),
                'banner': str (opcional),
                'start_date': str (ISO 8601),
                'end_date': str (ISO 8601),
                'discount_percentage': int
            },
            ...
        ]
    """
    api_url = (
        "https://store-site-backend-static.ak.epicgames.com/"
        "freeGamesPromotions?locale=pt-BR&country=BR&allowCountries=BR"
    )
    
    logger.info(f"📡 Acessando API: {api_url}")
    
    request = urllib.request.Request(
        api_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
    )
    
    with urllib.request.urlopen(request, timeout=10) as response:
        raw_data = response.read()
        if raw_data.startswith(b'\x1f\x8b'):
            raw_data = gzip.decompress(raw_data)
        data = json.loads(raw_data.decode('utf-8'))
    
    logger.info("✅ API respondeu com sucesso")
    
    elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
    logger.info(f"📦 Total de elementos no catálogo: {len(elements)}")
    
    games = []
    
    for game in elements:
        promotions = game.get('promotions', {})
        if promotions is None:
            promotions = {}
        promotional_offers = promotions.get('promotionalOffers', [])
        
        if not promotional_offers:
            continue
        
        game_data = {
            'title': game.get('title', 'Sem título'),
            'description': game.get('description', '').strip(),
            'slug': game.get('productSlug', ''),
            'url': f"https://store.epicgames.com/pt-BR/p/{game.get('productSlug', '')}",
            'original_price': _extract_price(game, 'originalPrice'),
            'discount_price': _extract_price(game, 'discountPrice'),
            'publisher': game.get('seller', {}).get('name', 'Epic Games'),
            'developer': _extract_custom_attribute(game, 'developerName'),
            'discount_percentage': _calculate_discount_percentage(game)
        }
        
        key_images = game.get('keyImages', [])
        for img in key_images:
            img_type = img.get('type')
            img_url = img.get('url')
            
            if img_type == 'Thumbnail' and img_url:
                game_data['thumbnail'] = img_url
            elif img_type == 'DieselStoreFrontWide' and img_url:
                game_data['banner'] = img_url
            elif img_type == 'OfferImageWide' and img_url and 'banner' not in game_data:
                game_data['banner'] = img_url
        
        if promotional_offers and promotional_offers[0].get('promotionalOffers'):
            offer = promotional_offers[0]['promotionalOffers'][0]
            game_data['start_date'] = offer.get('startDate', '')
            game_data['end_date'] = offer.get('endDate', '')
            
            if game_data['end_date']:
                game_data['end_date_formatted'] = _format_datetime(game_data['end_date'])
        
        games.append(game_data)
        logger.info(f"  ✓ {game_data['title']}")
    
    logger.info(f"🎮 Total de jogos gratuitos ativos: {len(games)}")
    
    return games


def _extract_price(game: Dict, price_type: str) -> str:
    """
    Extrai preço formatado do jogo
    
    Args:
        game: Dicionário com dados do jogo
        price_type: 'originalPrice' ou 'discountPrice'
        
    Returns:
        Preço formatado como string (ex: "R$ 99,99" ou "Grátis")
    """
    try:
        price = game.get('price', {}).get('totalPrice', {}).get('fmtPrice', {}).get(price_type)
        if price == '0':
            return 'Grátis'
        return price or 'N/A'
    except (KeyError, AttributeError):
        return 'N/A'


def _extract_custom_attribute(game: Dict, attribute_name: str) -> Optional[str]:
    """
    Extrai atributo customizado do jogo
    
    Args:
        game: Dicionário com dados do jogo
        attribute_name: Nome do atributo a extrair
        
    Returns:
        Valor do atributo ou None
    """
    try:
        custom_attributes = game.get('customAttributes', [])
        for attr in custom_attributes:
            if attr.get('key') == attribute_name:
                return attr.get('value')
        return None
    except (KeyError, AttributeError):
        return None


def _calculate_discount_percentage(game: Dict) -> int:
    """
    Calcula percentual de desconto
    
    Args:
        game: Dicionário com dados do jogo
        
    Returns:
        Percentual de desconto como inteiro (0-100)
    """
    try:
        price_info = game.get('price', {}).get('totalPrice', {})
        original = price_info.get('originalPrice', 0)
        discount = price_info.get('discountPrice', 0)
        
        if original > 0:
            percentage = int(((original - discount) / original) * 100)
            return percentage
        return 0
    except (KeyError, AttributeError, ZeroDivisionError, TypeError):
        return 0


def _format_datetime(iso_datetime: str) -> str:
    """
    Formata datetime ISO 8601 para formato brasileiro
    
    Args:
        iso_datetime: String ISO 8601 (ex: "2025-11-21T15:00:00.000Z")
        
    Returns:
        Data formatada (ex: "21/11/2025 às 12:00")
    """
    try:
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        from datetime import timedelta
        dt_br = dt - timedelta(hours=3)
        return dt_br.strftime("%d/%m/%Y às %H:%M")
    except (ValueError, AttributeError):
        return iso_datetime



if __name__ == "__main__":
    """
    Teste local do Lambda Handler
    Execute: python lambda_function.py
    """
    print("=" * 70)
    print("TESTE LOCAL - Epic Games Lambda Function")
    print("=" * 70)
    print()
    
    class FakeContext:
        request_id = "local-test-12345"
        function_name = "epic-games-scraper"
        memory_limit_in_mb = 128
    
    result = lambda_handler({}, FakeContext())
    
    print("\n" + "=" * 70)
    print("RESULTADO DA EXECUÇÃO")
    print("=" * 70)
    print(f"\n Status Code: {result['statusCode']}")
    print(f"\n Headers:")
    for key, value in result['headers'].items():
        print(f"   {key}: {value}")

    print(f"\n Body (JSON formatado):")
    print("-" * 70)

    body_data = json.loads(result['body'])
    print(json.dumps(body_data, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("Teste concluído!")
    print("=" * 70)