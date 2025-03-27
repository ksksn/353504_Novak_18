import React from "react";
import TrainersPage from "../trainers/TrainersPage";
import Requests from "./Requests";

const AdminPage = () => {
    return(
        <div className = "mainForm">
            <TrainersPage/>
            <div style={{width:"100%"}}>
            <div className = {"taskListForm"}>
                <h1 className="taskHeader"> Входящие запросы: </h1>
                <Requests nickname = "Armria"/>
            </div>
        </div>
        </div>
        
    )
}

export default AdminPage