import ccxt
import pandas as pd
import time

# Configuración de API
api_key = "yI2JN6jOeIjjy0XdoLuAqElcsGGNZNLvcQdwxIYKwVmRBWzdx8PxOV8vDoW9A0N3"
api_secret = "3Ffwnib0FK6kU3Ec638t6CKMIsAAhGuCVpsiQijjr6qZyuPjXALAOqxdt9PvgR2U"

# Conexión con Binance
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
})

# Parámetros
symbol = "BTC/USDC"  # Formato correcto para Binance
timeframe = "1h"
balance_percentage = 0.1
sma_short_period = 7
sma_long_period = 21


def fetch_candles():
    """Obtiene los últimos datos de velas"""
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe, limit=sma_long_period + 5)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception as e:
        print(f"Error al obtener velas: {e}")
        return pd.DataFrame()


def calculate_sma(df):
    """Calcula las medias móviles"""
    df['SMA_07'] = df['close'].rolling(window=sma_short_period).mean()
    df['SMA_21'] = df['close'].rolling(window=sma_long_period).mean()
    return df


def get_balance():
    try:
        balance = exchange.fetch_balance({'type': 'spot'})
        usdt_balance = balance['free'].get('USDC', 0)
        print(f"Balance actual: {usdt_balance} USDC")
        return usdt_balance
    except Exception as e:
        print(f"Error al obtener balance: {e}")
        return 0


def place_order(side, amount):
    """Coloca una orden de compra o venta"""
    try:
        price = exchange.fetch_ticker(symbol)['last']
        quantity = amount / price if side == "buy" else amount
        order = exchange.create_market_order(symbol, side, quantity)
        print(f"Orden {side} ejecutada: {order}")
    except Exception as e:
        print(f"Error al colocar orden: {e}")


def run_bot():
    """Ejecuta el bot en un loop"""
    last_signal = None

    while True:
        try:
            balance = get_balance()
            df = fetch_candles()
            if df.empty:
                time.sleep(60)
                continue

            df = calculate_sma(df)
#            amount = balance * balance_percentage
#            place_order("buy", amount)
#            btc_balance = exchange.fetch_balance()['free'].get('BTC', 0)
#            place_order("sell", btc_balance)
            # Estrategia de cruce de medias móviles
            if df['SMA_07'].iloc[-2] < df['SMA_21'].iloc[-2] and df['SMA_07'].iloc[-1] > df['SMA_21'].iloc[-1]:
                if last_signal != "buy" and balance > 10:
                    amount = balance * balance_percentage
                    place_order("buy", amount)
                    last_signal = "buy"

            elif df['SMA_07'].iloc[-2] > df['SMA_21'].iloc[-2] and df['SMA_07'].iloc[-1] < df['SMA_21'].iloc[-1]:
                btc_balance = exchange.fetch_balance()['free'].get('BTC', 0)
                if last_signal != "sell" and btc_balance > 0.0001:
                    place_order("sell", btc_balance)
                    last_signal = "sell"

            time.sleep(60)

        except Exception as e:
            print(f"Error en ejecución: {e}")
            time.sleep(60)

# Ejecutar el bot
run_bot()
