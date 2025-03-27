import React, { useEffect, useState } from "react";
import CreatedContests from "./CreatedContests";
import "../contests/tasks/taskList/TaskList.css";
import "./styles/ModalContest.css";
import ContestService from "../../API/ContestService";
import SubmitContest from "../../API/CreateContest";

const TrainersPage = () => {
  const [showModal, setShowModal] = useState(false);
  const [contestData, setContestData] = useState({
    name: "",
    start_time: "",
    duration: "",
  });
  const [ownContests, setOwnContests] = useState();
  const [a, setA] = useState(false)

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    if( value!="")
      setContestData({ ...contestData, [name]: value });
  };

  const handleModalOpen = () => {
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
  };

  useEffect(() => {
    async function fetchOwnContests() {
      let contests = await ContestService.handleOwnContest();
      setOwnContests(contests)
    }
    if (a === true) {
      fetchOwnContests();
    }
    setA(true)
  }, [a]);

  async function createContest(e){
    console.log(contestData)
    await SubmitContest.handleModalSubmit(contestData)
    window.location.reload(true)
  }

  function showOwnContests() {
    if (!ownContests) {
      return <></>;
    }
    return ownContests.map(contest => 
      <CreatedContests contestName={contest.name} contestId={contest.id}/>
    )
  }

  return (
    <div style={{ width: "100%" }}>
      <div className={"taskListForm"}>
        <h1 className="taskHeader"> Созданные соревнования: </h1>
        {showOwnContests()}
        <button className="darkButton" onClick={handleModalOpen}>
          Создать контест
        </button>
        {showModal && (
          <div className="modal">
            <div className="modal-content">
              <span className="close" onClick={handleModalClose}>
                &times;
              </span>
              <h2 className="header">Создание контеста</h2>
              <form>
                <label>
                  Название:
                  <input className="field" 
                    type="text"
                    name="name"
                    value={contestData.name}
                    onChange={handleInputChange}
                  />
                </label>
                <label>
                  Дата начала:
                  <input className="field" 
                    type="datetime-local"
                    name="start_time"
                    value={contestData.start_time}
                    onChange={handleInputChange}
                  />
                </label>
                <label>
                  Длительность:
                  <input className="field" 
                    type="time"
                    name="duration"
                    value={contestData.duration}
                    onChange={handleInputChange}
                  />
                </label>
                <button type="button" onClick={createContest}>
                  Создать
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainersPage;
