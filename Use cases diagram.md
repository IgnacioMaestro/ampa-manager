# Use cases diagram

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

![](www.plantuml.com/plantuml/png/XOz12i8m44NtFSKisqMl88s22rVY3K9cR0UJ2IGJmTjheOje0sxVVo5lfgmsQGc-ytHNq0Y9vqK1EP5JZjBrDvevAoKusy3-DNIzGOJJmXvNttxpgqqa-ZlapBF0qSh3E1VB9cpoKFrXdFAJTNrqYInWfK86mmUDum7sKTNMpgkDEhIj_4rkjJHBzsTC95Y2VmC0)
