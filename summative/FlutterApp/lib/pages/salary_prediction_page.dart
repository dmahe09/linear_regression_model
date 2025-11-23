import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'result_page.dart';

class SalaryPredictionPage extends StatefulWidget {
  const SalaryPredictionPage({super.key});

  @override
  _SalaryPredictionPageState createState() => _SalaryPredictionPageState();
}

class _SalaryPredictionPageState extends State<SalaryPredictionPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _experienceController = TextEditingController();
  String _gender = 'Male';
  String _education = 'Bachelor';
  String _jobTitle = 'Manager';
  String _location = 'Urban';
  String _errorMessage = '';

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  child: Icon(icon, color: Theme.of(context).colorScheme.primary, size: 20),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.onSurface,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildNameField() {
    return TextFormField(
      controller: _nameController,
      decoration: InputDecoration(labelText: 'Name'),
      validator: (value) => value!.isEmpty ? 'Please enter a name' : null,
    );
  }

  Widget _buildAgeField() {
    return TextFormField(
      controller: _ageController,
      decoration: InputDecoration(labelText: 'Age'),
      keyboardType: TextInputType.number,
      validator: (value) {
        if (value!.isEmpty) return 'Please enter an age';
        final age = int.tryParse(value);
        if (age == null || age < 18 || age > 100) return 'Age must be 18-100';
        return null;
      },
    );
  }

  Widget _buildGenderDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _gender,
      items: ['Male', 'Female', 'Other'].map((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
      onChanged: (value) => setState(() => _gender = value!),
      decoration: InputDecoration(labelText: 'Gender'),
    );
  }

  Widget _buildEducationDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _education,
      items: ['High School', 'Bachelor', 'Master', 'PhD'].map((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
      onChanged: (value) => setState(() => _education = value!),
      decoration: InputDecoration(labelText: 'Education'),
    );
  }

  Widget _buildExperienceField() {
    return TextFormField(
      controller: _experienceController,
      decoration: InputDecoration(labelText: 'Years of Experience'),
      keyboardType: TextInputType.number,
      validator: (value) {
        if (value!.isEmpty) return 'Please enter experience';
        final exp = double.tryParse(value);
        if (exp == null || exp < 0) return 'Experience must be non-negative';
        return null;
      },
    );
  }

  Widget _buildJobTitleDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _jobTitle,
      items: ['Manager', 'Developer', 'Analyst', 'Designer'].map((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
      onChanged: (value) => setState(() => _jobTitle = value!),
      decoration: InputDecoration(labelText: 'Job Title'),
    );
  }

  Widget _buildLocationDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _location,
      items: ['Urban', 'Rural', 'Suburban'].map((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
      onChanged: (value) => setState(() => _location = value!),
      decoration: InputDecoration(labelText: 'Location'),
    );
  }

  Future<void> _predictSalary() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _errorMessage = '');
      try {
        // Create a SalaryPredictionRequest object
        final request = SalaryPredictionRequest(
          name: _nameController.text,
          age: int.parse(_ageController.text),
          gender: _gender,
          jobTitle: _jobTitle,
          education: _education,
          yearsOfExperience: double.parse(_experienceController.text),
          location: _location,
        );
        
        final response = await ApiService.predictSalary(request);
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => EnhancedResultPage(response: response),
          ),
        );
      } catch (e) {
        setState(() => _errorMessage = _formatError(e));
      }
    }
  }

  String _formatError(dynamic error) {
    if (error is Exception) {
      if (error.toString().contains('SocketException')) {
        return 'Unable to connect to the server. Please check your internet connection.';
      }
      return 'An error occurred: ${error.toString()}';
    }
    return 'Unexpected error occurred.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Salary Predictor'),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildSectionCard(
                  title: "Personal Details",
                  icon: Icons.person,
                  children: [
                    _buildNameField(),
                    const SizedBox(height: 20),
                    _buildAgeField(),
                    const SizedBox(height: 20),
                    _buildGenderDropdown(),
                  ],
                ),
                const SizedBox(height: 20),
                _buildSectionCard(
                  title: "Professional Details",
                  icon: Icons.work,
                  children: [
                    _buildEducationDropdown(),
                    const SizedBox(height: 20),
                    _buildExperienceField(),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        Expanded(child: _buildJobTitleDropdown()),
                        const SizedBox(width: 15),
                        Expanded(child: _buildLocationDropdown()),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 30),
                ElevatedButton(
                  onPressed: _predictSalary,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 15),
                    child: Text('Predict My Salary'),
                  ),
                ),
                if (_errorMessage.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 10),
                    child: Text(
                      _errorMessage,
                      style: TextStyle(color: Colors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}