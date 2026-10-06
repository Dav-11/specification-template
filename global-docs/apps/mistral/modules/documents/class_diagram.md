# Document Sequence diagram

## Diagram

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
      +String beakColor
      +swim()
      +quack()
    }
    class Fish{
      -int sizeInFeet
      -canEat()
    }
    class Zebra{
      +bool is_wild
      +run()
    }
```

## Description

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean et felis dapibus leo tempor placerat. Pellentesque interdum nibh vitae purus placerat eleifend. In venenatis condimentum commodo. Proin porttitor erat in nisi gravida hendrerit. Maecenas fringilla, arcu et consequat hendrerit, orci nunc egestas quam, id elementum odio augue ut massa. Sed in imperdiet ligula. Praesent nunc massa, interdum id metus eu, tincidunt mollis ante.