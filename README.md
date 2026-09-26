# Limitless Watch: self-hosted Limitless scraper for Discord

Limitless Watch is a proof-of-concept bot designed send updates to a Discord server whenever [Limitless](limitlesstcg.com) updates one of its sets databases or tournament databases.

## Usage

This guide assumes that you have already created a webhook. To learn how to do so, a visual guide is available in the readme at [fadwen/FeedCord](https://github.com/fadwen/FeedCord).

1. Copy `config-example.json` to `config.json`.
2. Edit `config.json` according to your preferences. It should contain an array of dictionaries, each describing a webhook. In the example file provided, this array only has one element, but you can have multiple elements, for example in order to serve more than one Discord server. Each dictionary in the array should contain:
  - `"webhook_url"` (string): the URL of the webhook you have created
  - `"webhook_parameters"` (dictionary, optional): a dictionary containing any combination of the following:
    - `"username"` (string or null, optional): the username to use on Discord
    - `"avatar_url"` (string or null, optional): a url pointing to the profile picture to use on Discord
	- `"color"` (integer or null, optional): the color code for the embeds to send
  - `"sleep_hours"` (integer, optional): the time (in hours) to wait between consecutive updates. By default, it is 24. Note: this will be read **only for the first** webhook, and applied to every webhook
  - `"filter_mode"` (string): can be `"whitelist"` or `"blacklist"`
  - `"filter_list"` (array of strings): if `"filter_mode"` is set to `"whitelist"`, this is the list of updates to send to Discord. If `"filter_mode"` is set to `"blacklist"`, all updates will be sent, except those in this list. The strings that can be included in this array are:
    - `"ptcg intl"`, for new [international](https://limitlesstcg.com/cards) sets and set code changes in the Pokémon TCG database
    - `"ptcg intl promo"`, for [international](https://limitlesstcg.com/cards) sets in the Pokémon TCG database that have cards added to them (tipically, these are promo sets)
    - `"ptcg jpn"`, for new [Japanese](https://limitlesstcg.com/cards/jp) sets and set code changes in the Pokémon TCG database
    - `"ptcg jpn promo"`, for [Japanese](https://limitlesstcg.com/cards/jp) sets in the Pokémon TCG database that have cards added to them (tipically, these are promo sets)
    - `"ptcg tournament"`, for new [tournament results data](https://limitlesstcg.com/tournaments) in the Pokémon TCG database
    - `"vgc tournament"`, for new tournament results data in the [Pokémon VGC database](https://limitlessvgc.com/tournaments)
    - `"ptcg pocket"`, for new sets and set code changes in the [Pokémon TCG Pocket database](https://pocket.limitlesstcg.com/cards)
    - `"ptcg pocket promo"`, for sets in the [Pokémon TCG Pocket database](https://pocket.limitlesstcg.com/cards) that have cards added to them (tipically, these are promo sets)
    - `"onepiece product"`, for new [products](https://onepiece.limitlesstcg.com/cards) (booster packs and starter decks) in the One Piece TCG database *(currently unsupported by Limitless Watch)*
    - `"onepiece promo"`, for new [promos](https://onepiece.limitlesstcg.com/cards/promos) in the One Piece TCG database *(currently unsupported by Limitless Watch)*
    - `"onepiece tournament"`, for new [tournament results data](https://onepiece.limitlesstcg.com/tournaments) in the One Piece TCG database
	- `"lorcana"`, for new [Lorcana](https://limitlesstcg.com/lorcana) sets
	- `"riftbound"`, for new [Riftbound](https://limitlesstcg.com/riftbound) sets
	- `"swu"`, for new [Star Wars Unlimited](https://limitlesstcg.com/swu) sets
	- `"bandai/dcg"`, for new [Digimon](https://limitlesstcg.com/bandai/dcg) sets
	- `"bandai/fw"`, for new [DBS: Fusion World](https://limitlesstcg.com/bandai/fw) sets 
	- `"bandai/dbs"`, for new [DBS: Masters](https://limitlesstcg.com/bandai/dbs) sets 
	- `"bandai/bss"`, for new [Battle Spirits Saga](https://limitlesstcg.com/bandai/bss) sets 
	- `"bandai/gundam"`, for new [Gundam Card Game](https://limitlesstcg.com/bandai/bss) sets 
3. Start `limitless_watch.py` in the background. It will scrape Limitless daily and send updates whenever it finds them. Add `--verbose` to see print logs on the console.

## Contributing

If you'd like to contribute, here is a to-do list:

- add better error handling and logs
- add checks to detect changes in page layout on the Limitless website that would prevent the scraper from running properly

Additional items in the to-do list may appear in the issues tab.

## Acknowledgements

I would like to thank:

- Legendary, for letting me test this bot in the [JustInBasil Discord server](https://www.justinbasil.com/discord) (as well as the late JustInBasil for creating that community, it is truly a wonderful place)
- [Eskaven](https://github.com/Eskaven-dot-dev), for providing feedback
- [Qolors](https://github.com/Qolors), for creating [FeedCord](https://github.com/Qolors/FeedCord), and [fadwen](https://github.com/fadwen), for maintaining [their fork](https://github.com/fadwen/FeedCord): using FeedCord is what inspired me to make this bot.
- The [Limitless staff](https://limitlesstcg.com/about#staff), for maintaining a service worth making this bot for.