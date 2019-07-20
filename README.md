# lifxtools

`python3 -m lifxtools` is where the action is at

_[NOTE]: This readme is a work-in-progress. If you require any specific information, please submit a github issue. I will try my best to address any questions you have in this readme once I get the chance. Thanks! :)_

## Notable usages
### average_screen_color.py
(Ultra-slow fade mode)
Stanley Kubrick's A Clockwork Orange is well enhanced by the effect of average_screen_color.py; first few minutes of the film are of particularly strong effect.

(Slow fade mode)
Blade Runner (1997). Movie full of both muted and vibrant tones. Takes full advantage of the vividness of the colour of lifx bulbs

(Game fade mode)
Half-Life 2: Episode 1. The first few levels of this game are truly awesome with live colour averages.

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

### Add preferences for monitor refresh related
With the addition of benchmarking capabilities available to the user, this will allow users to compare their color average processing time with the refresh rate of their displays. Ideally, this number should be as close to matching as possible (with consideration for network speed also)

### Don't send packets if colour is identical to last sent colour
This has the intention of saving network bandwidth (and potenially a small amount of processing time)
