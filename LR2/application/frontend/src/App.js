import React from 'react';
import "./App.css";
import Home from "./components/home/HomePage";
import {Route, Routes} from "react-router-dom";
import AuthRootComponent from "./components/authorization/Routes";
import Header from "./components/Header/Header";
import Contests from "./components/contests/contestsPage/ContestsPage";
import Task from "./components/contests/tasks/taskPage/TaskPage";
import TaskList from './components/contests/tasks/taskList/TaskList';
import Submissions from './components/contests/solutions/Solutions';
import Standings from './components/contests/standings/Standings'
import TrainersPage from './components/trainers/TrainersPage';
import AdminPage from './components/admin/AdminPage';

function App() {
  return (
    <div className='app'>
      <Header />
       <Routes>
            <Route path = "/" element = {<Home/>}/>
            <Route path = "/contests" element = {<Contests/>}/>
            <Route path = "/contest/:id" element = {<TaskList/>}/>
            <Route path = "/contest/:id/problem/:problemId" element = {<Task/>}/>
            <Route path ="/contest/:id/standings" element={<Standings/>}/>
            <Route path = "/submissions/:problemId" element = {<Submissions/>}/>
            <Route path = "/enter" element = {<AuthRootComponent/>}/>
            <Route path = "/register" element = {<AuthRootComponent/>}/>
            <Route path="/edu" element = {<TrainersPage/>}/>
            <Route path="/admin" element = {<AdminPage/>}/>
        </Routes>
    </div>
  );
}

export default App;
