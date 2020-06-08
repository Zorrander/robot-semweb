#include <QObject>
#include <QString>
#include <iostream>

#include "include/cobot_behavior/knowledge.hpp"

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "cobot_msgs/srv/export.hpp"

Knowledge::Knowledge(QObject *parent) :
    QObject(parent)
{
    node = rclcpp::Node::make_shared("minimal_client");
    client = node->create_client<cobot_msgs::srv::Export>("export_onto");
}

QString Knowledge::filename()
{
    return m_filename;
}

QStringListModel *Knowledge::tasks()
{
    QStringListModel *model = new QStringListModel;
    QStringList list;
    list << "test" << "test2" << "test3";
    model->setStringList(list);
    return model;
}


void Knowledge::setFilename(const QString &value)
{
    if (value != m_filename) {
       m_filename = value;
       emit filenameChanged();
    }
}

void Knowledge::export_ontology(const QString qstr_filename){
    auto request = std::make_shared<cobot_msgs::srv::Export::Request>();
    request->filename = qstr_filename.toUtf8().constData();
    auto result = client->async_send_request(request);
    rclcpp::spin_some(node);
}

