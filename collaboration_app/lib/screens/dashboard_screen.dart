import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import 'login_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _teams = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchTeams();
  }

  Future<void> _fetchTeams() async {
    try {
      final response = await ApiService.get('api/teams/');
      if (response.statusCode == 200) {
        setState(() {
          _teams = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      print('Fetch Error: e');
      setState(() => _isLoading = false);
    }
  }

  void _logout() async {
    await Provider.of<AuthProvider>(context, listen: false).logout();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('My Teams', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(icon: Icon(Icons.logout), onPressed: _logout),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _teams.isEmpty
              ? Center(child: Text('You are not currently assigned to any team.'))
              : ListView.builder(
                  padding: EdgeInsets.all(16.0),
                  itemCount: _teams.length,
                  itemBuilder: (context, index) {
                    final team = _teams[index];
                    return Card(
                      elevation: 4,
                      margin: EdgeInsets.only(bottom: 16.0),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      child: ListTile(
                        contentPadding: EdgeInsets.all(16),
                        leading: CircleAvatar(
                          child: Icon(Icons.group, color: Colors.white),
                          backgroundColor: Colors.blueAccent,
                        ),
                        title: Text(team['name'], style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        subtitle: Text('${team['groupmembers']?.length ?? 0} Members active'),
                        trailing: Icon(Icons.chevron_right),
                        onTap: () {
                          // Navigate to Team Board internally naturally
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
