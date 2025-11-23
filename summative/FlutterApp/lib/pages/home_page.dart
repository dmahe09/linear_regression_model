import 'package:flutter/material.dart';
import 'salary_prediction_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController experienceController = TextEditingController();
  String? errorText;

  Future<void> predictSalary() async {
    final experience = double.tryParse(experienceController.text);

    if (experience == null || experience < 0 || experience > 50) {
      setState(() {
        errorText = "Enter valid experience (0 - 50)";
      });
      return;
    }

    try {
      // Open the detailed prediction page (contains the full form and API integration).
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const SalaryPredictionPage()),
      );
    } catch (e) {
      setState(() {
        errorText = "Could not open prediction page.";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Salary Predictor")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(
              "Enter Years of Experience:",
              style: TextStyle(fontSize: 18),
            ),
            TextField(
              controller: experienceController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                hintText: "e.g. 3.5",
                errorText: errorText,
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: predictSalary,
              child: Text("Predict"),
            ),
          ],
        ),
      ),
    );
  }
}