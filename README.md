# AMPAMembersManager

<!--
@startuml
class Family {
  FirstSurname : String
  SecondSurname : String
}
class Parent {
  Name : String
  Surname: String
} 

class Child {
  Name : String
} 

class BankAccount
class Course
abstract class "Activity"
class Familiar
class Individual
Activity <|-- Familiar
Activity <|-- Individual
Familiar o-up- Family
Activity o-up- BankAccount
Individual o-up- Child
Family *-- "N" Child
Family *-- "1..2" Parent
Parent *-- "0..N" BankAccount
Child o-- "1" Course
Family o-- BankAccount
@enduml
-->

![](firstDiagram.svg)
![](https://www.plantuml.com/plantuml/svg/RP11IyGm48Nl-HL3ZaABUXGFkmeBNXQXls1CWWRJH9A9KDJ_Racc9BezbRxtljVEEoJ2I7bsGZbC2KuuMxV0bm0usPXeoj7ZRE0E9ehMlwxwP5Jm-iBuuOPdZCPJQJZ_8vbf20Y67j-iqutPIJoWVpyg5RAdZGav9YFm9L54HL1LULHaFoqjih_8OkJN9wzNMsTqOal2_VSmjDmVkSzl2GX3_c1WQV6gzl_PM3RBcO8tlbhRvLdkY3VZU2jvI54VrRWUnnNeFr672uMIF0bt5RNF7epNUNQ_)
