          _________   ___________________________.____     
         /   _____/  /  _  \__    ___/\__    ___/|    |    
         \_____  \  /  /_\  \|    |     |    |   |    |    
         /        \/    |    \    |     |    |   |    |___ 
        /_______  /\____|__  /____|     |____|   |_______ \
                \/         \/                            \/

**SA**lesforce **T**esting **T**oo**L** or Sattl is a CLI that runs tests from a provided folder.

```shell
sattl --timeout 900 --domain my-domain your/sattl_tests/location/
```
In the command above, we run all test cases found at `your/sattl_tests/location/`. Here is what Sattl is going to do:
- for each Test Case found, meaning folder, Sattl will list all files in it and group them by their prefix to create
Test Steps
- for each Test Step Sattl will:
  * sequentially create objects found in manifests (if there are any)
  * test if objects contained in the assert file (if there is one) exist and match. The whole assert is tested until
  a timeout is exceeded (here 900 seconds) and in that case the test stops there and print the difference found
  * delete all objects contained in the delete file (if there is one)

We can also run only a specific Test Case by using a command like
```shell
sattl --domain my-domain --test-case your/sattl_tests/your-test-case/
```

# Jargon

### Manifest(s)
YAML file containing one or more objects to be created in Salesforce

### Assert
YAML file containing one or more objects that must exist and match in Salesforce

### Delete
YAML file containing one or more objects that must be deleted in Salesforce

### Test Step
Set of as many Manifests wanted and at most one Assert and/or Delete. A Test Step could consist of only Manifests,
only and Assert, or only one Delete

### Test Case
Set of Test Steps. Test Steps are ordered alphabetically and grouped by their prefix, whicih is the starting
string/number before the character -

# Example of a Test Case

Let us imagining we have the following
```
.
└── test-case1
    ├── 00-delete.yaml
    ├── 01-account.yaml
    ├── 01-course-and-section.yaml
    ├── 01-enrollment.yaml
    ├── 02-assert.yaml
    └── 02-case.yaml
    ├── 02-delete.yaml
```
We are going to look at the different parts of this Test Case

## Test Step 00

### Manifests
None

### Assert
None

### Delete
##### **`00-delete.yaml`**
```yaml
type: Account
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
---
type: PlatformAccount
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
```

Sattl deletes the Account object with UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302, then the PlatformAccount object
with UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302.

## Test Step 01

### Manifests

##### **`01-account.yaml`**
```yaml
type: Account
externalID:
  UUID__c: aaa52d9a-520c-4c7e-bbbb-3b6fde10b302
sis_first_name__c: John
sis_last_name__c: Doe
University_Email__c: jdoe@test.com
relations:
  recordTypeID:
    type: RecordType
    name: SIS Student
```

Sattl creates the Account object with UUID__c = aaa52d9a-520c-4c7e-bbbb-3b6fde10b302 and all the specified fields.

##### **`01-course-and-section.yaml`**
```yaml
type: Course__c
externalID:
  Slug__c: MT-105A-03
name: Sample Course
course_code__c: MT-105A-03
course_title__c: Mathematics 1
course_type__c: SIS
credits__c: 15.0
domain__c: ul-umt
---
type: Section__c
externalID:
  Slug__c: MT-105A-03:HOLDING:2020/1_05
name: Sample Section
code__c: HOLDING
non_lms__c: False
semester__c: 2020/1_05
relations:
  course__c:
    type: Course__c
    slug__c: MT-105A-03
```

Sattl creates the Course__c object with Slug__c = MT-105A-03 and all the specified fields, then the object Section__c
with Slug__c = MT-105A-03:HOLDING:2020/1_05 with its fields as well.

##### **`01-enrollment.yaml`**
```yaml
type: Enrollment__c
externalID:
  Slug__c: aaa52d9a-520c-4c7e-bbbb-3b6fde10b302:MT-105A-03:HOLDING:2020/1_05
name: Sample Enrollment
status__c: Enrolled
relations:
  section__c:
    type: Section__c
    Slug__c: MT-105A-03:HOLDING:2020/1_05
  Student__c:
    type: Account
    UUID__c: aaa52d9a-520c-4c7e-bbbb-3b6fde10b302
```

Sattl creates the Enrollment__c object with Slug__c = aaa52d9a-520c-4c7e-bbbb-3b6fde10b302:MT-105A-03:HOLDING:2020/1_05
and all the specified fields.

### Assert
None

### Delete
None

## Test Step 02

### Manifests
##### **`02-case.yaml`**
```yaml
type: Case
externalID:
  Change_Active_ID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
change_id__c: new:account:fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
approval__c: Approved
status: Closed-Approved
reason: SIS
change_object__c: Account
origin: PortAuthority
Platform_Host__c: a2z7A0000007v94QAA
new_raw__c: |
{
  "username": "pknight+patest8@2u.com",
  "first_name": "Hector",
  "last_name": "Hibiscus",
  "email": "pknight+patest8@2u.com",
  "university_id": "1800008",
  "uuid": "fbd52d9a-520c-4c7e-b0ba-3b6fde10b302",
}
relations:
  RecordTypeID:
    type: RecordType
    Name: Port Authority Case
```

Sattl creates the Case object with Change_Active_ID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302 and all the specified
fields.

### Assert
##### **`02-assert.yaml`**
```yaml
type: Account
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
sis_first_name__c: John
sis_last_name__c: Smith
University_Email__c: smith+patest8@2u.com
relations:
  recordTypeID:
    type: RecordType
    name: SIS Student
---
type: PlatformAccount
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
Platform_Host__c: a2z7A000000MGr1QAG
Status__c: Active
University_ID__c: 1800008
Namespace_University_ID__c: 1800008-UD
relations:
  recordTypeID:
    type: RecordType
    name: SIS Student
    Student__c:
        type: Account
        UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
```

Sattl asserts the Account object with UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302 exists and all its fields match
the values provided. It then asserts the same for the PlatformAccount object with
UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302.

### Delete
##### **`02-delete.yaml`**
```yaml
type: Account
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
---
type: PlatformAccount
externalID:
  UUID__c: fbd52d9a-520c-4c7e-b0ba-3b6fde10b302
```

Sattl deletes the Account object with UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302 then the PlatformAccount object
with UUID__c = fbd52d9a-520c-4c7e-b0ba-3b6fde10b302.