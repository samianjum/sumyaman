import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(const APSPortal());

class APSPortal extends StatelessWidget {
  const APSPortal({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: const Color(0xFF1B4332)),
      home: const MainGate(),
    );
  }
}

class MainGate extends StatefulWidget {
  const MainGate({super.key});
  @override
  State<MainGate> createState() => _MainGateState();
}

class _MainGateState extends State<MainGate> {
  Map? currentUser; // User data store karne ke liye

  void onLoginSuccess(Map data) {
    setState(() {
      currentUser = data;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Agar user login nahi hai to Login Page dikhao, warna Dashboard
    return currentUser == null 
        ? LoginPage(onLogin: onLoginSuccess) 
        : Dashboard(userData: currentUser!, onLogout: () => setState(() => currentUser = null));
  }
}

class LoginPage extends StatefulWidget {
  final Function(Map) onLogin;
  const LoginPage({super.key, required this.onLogin});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _idController = TextEditingController();
  DateTime selectedDate = DateTime(2010, 1, 1);
  bool loading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  Future<void> login() async {
    setState(() => loading = true);
    String role = _tabController.index == 0 ? "Student" : "Teacher";
    String dob = "${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}";
    
    try {
      final res = await http.get(Uri.parse("http://localhost:8080/login/$role/${_idController.text}/$dob"));
      final data = json.decode(res.body);
      if (data['success']) {
        widget.onLogin(data['data']);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Ghalat details! Check database.")));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("API Error! Terminal 2 check karein.")));
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1B4332),
      body: Center(
        child: Container(
          width: 350, padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.school, size: 60, color: Color(0xFF1B4332)),
              const Text("APS OKARA", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              TabBar(controller: _tabController, labelColor: Colors.black, tabs: const [Tab(text: "Student"), Tab(text: "Teacher")]),
              const SizedBox(height: 20),
              TextField(controller: _idController, decoration: const InputDecoration(labelText: "B-Form / CNIC", border: OutlineInputBorder())),
              const SizedBox(height: 10),
              TextButton(onPressed: () async {
                final d = await showDatePicker(context: context, initialDate: selectedDate, firstDate: DateTime(1990), lastDate: DateTime.now());
                if (d != null) setState(() => selectedDate = d);
              }, child: Text("DOB: ${selectedDate.toLocal()}".split(' ')[0])),
              const SizedBox(height: 20),
              loading ? const CircularProgressIndicator() : ElevatedButton(onPressed: login, child: const Text("LOGIN")),
            ],
          ),
        ),
      ),
    );
  }
}

class Dashboard extends StatelessWidget {
  final Map userData;
  final VoidCallback onLogout;
  const Dashboard({super.key, required this.userData, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(userData['full_name']), actions: [IconButton(onPressed: onLogout, icon: const Icon(Icons.logout))]),
      body: GridView.count(
        padding: const EdgeInsets.all(20),
        crossAxisCount: 2, crossAxisSpacing: 10, mainAxisSpacing: 10,
        children: [
          _card("Attendance", Icons.check_circle, Colors.green),
          _card("Diary", Icons.book, Colors.blue),
          _card("Results", Icons.grade, Colors.orange),
          _card("Notices", Icons.notifications, Colors.purple),
        ],
      ),
    );
  }

  Widget _card(String t, IconData i, Color c) {
    return Card(
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(i, size: 40, color: c), Text(t)]),
    );
  }
}
