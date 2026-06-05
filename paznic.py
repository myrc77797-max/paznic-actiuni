name: Paznic Actiuni

on:
  schedule:
    - cron: '*/15 13-20 * * 1-5'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  paznic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install alpaca-py requests
      - run: python paznic.py
        env:
          ALPACA_API_KEY: ${{ secrets.ALPACA_API_KEY }}
          ALPACA_SECRET_KEY: ${{ secrets.ALPACA_SECRET_KEY }}
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      - name: Salveaza starea
        run: |
          git config user.name "paznic-bot"
          git config user.email "paznic@bot.local"
          git add stare.json
          git commit -m "actualizare stare" || echo "nimic de comis"
          git push
