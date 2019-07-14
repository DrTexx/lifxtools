# lifxtools

`python3 -m lifxtools` is where the action is at

_[NOTE]: This readme is a work-in-progress. If you require any specific information, please submit a github issue. I will try my best to address any questions you have in this readme once I get the chance. Thanks! :)_

## Notable usages
### average_screen_color.py
(Ultra-slow fade mode)
Stanley Kubrick's A Clockwork Orange is well enhanced by the effect of average_screen_color.py; first few minutes of the film are of particularly strong effect.

(Slow fade mode)
Blade Runner (1997). Movie full of both muted and vibrant tones. Takes full advantage of the vividness of the colour of lifx bulbs

## Todo
### Public Transport API Intergration
Intergration for multiple public transport APIs. This will involve making a package to translate multiple APIs to the general format (which is likely object-based)

Planned APIs to intergrate:
- PTV (Public Transport Victoria)

### Better colours for "Dusk and Dawn" lifx bulbs
The plan:

| color condition | effect        |
| ---             | ---           |
| blue > red      | cooler light  |
| blue == red     | neutral light |
| blue < red      | warmer light  |
