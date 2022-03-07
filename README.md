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
